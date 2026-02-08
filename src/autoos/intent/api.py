"""
FastAPI REST API - Intent submission and workflow management

Provides HTTP endpoints for external systems to interact with AUTOOS.
"""

from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import os

from autoos.core.models import RiskLevel, WorkflowState
from autoos.memory.session_memory import SessionMemory
from autoos.memory.working_memory import WorkingMemory
from autoos.infrastructure.event_bus import EventBus
from autoos.infrastructure.logging import get_logger, setup_logging
from autoos.infrastructure.metrics import get_metrics_collector, initialize_metrics
from autoos.auth.middleware import (
    AuthMiddleware,
    require_auth,
    require_subscription,
    require_rate_limit,
    security
)
from autoos.payment.stripe_service import StripeService

# Initialize logging
setup_logging(
    level=os.getenv("LOG_LEVEL", "INFO"),
    log_format=os.getenv("LOG_FORMAT", "json"),
)

logger = get_logger(__name__)

# Initialize metrics
metrics = initialize_metrics()

# Create FastAPI app
app = FastAPI(
    title="AUTOOS - Omega Edition API",
    description="The Automation Operating System - Intelligence Orchestration API",
    version="1.0.0",
)

# Initialize components (will be properly initialized in main)
session_memory: Optional[SessionMemory] = None
working_memory: Optional[WorkingMemory] = None
event_bus: Optional[EventBus] = None
stripe_service: Optional[StripeService] = None


# ============================================================================
# Request/Response Models
# ============================================================================


class IntentRequest(BaseModel):
    """Intent submission request"""

    intent: str = Field(..., description="Natural language intent")
    context: Dict[str, Any] = Field(
        default_factory=dict, description="Additional context"
    )
    priority: str = Field(default="normal", description="Priority level")


class IntentResponse(BaseModel):
    """Intent submission response"""

    workflow_id: str
    status: str
    estimated_cost: float
    estimated_time: float
    message: str


class WorkflowStatusResponse(BaseModel):
    """Workflow status response"""

    workflow_id: str
    status: str
    created_at: str
    completed_at: Optional[str]
    cost: float
    confidence: Optional[float]
    steps_completed: int
    steps_failed: int


class AuditTrailResponse(BaseModel):
    """Audit trail response"""

    workflow_id: str
    entries: List[Dict[str, Any]]
    total_entries: int


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    timestamp: str
    version: str
    components: Dict[str, str]


# ============================================================================
# Authentication
# ============================================================================


def verify_api_key(x_api_key: str = Header(...)) -> str:
    """
    Verify API key

    Args:
        x_api_key: API key from header

    Returns:
        User ID

    Raises:
        HTTPException: If API key is invalid
    """
    # Simplified authentication - production would use proper key management
    valid_keys = {
        "dev-key-123": "user-dev",
        "prod-key-456": "user-prod",
    }

    user_id = valid_keys.get(x_api_key)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return user_id


# ============================================================================
# API Endpoints
# ============================================================================


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint

    Returns system health status
    """
    components = {
        "api": "healthy",
        "session_memory": "healthy" if session_memory else "not_initialized",
        "working_memory": "healthy" if working_memory else "not_initialized",
        "event_bus": "healthy" if event_bus else "not_initialized",
    }

    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        components=components,
    )


@app.get("/metrics")
async def get_metrics():
    """
    Prometheus metrics endpoint

    Returns metrics in Prometheus format
    """
    metrics_data = metrics.export_metrics()
    return StreamingResponse(
        iter([metrics_data]),
        media_type=metrics.get_content_type(),
    )


@app.post("/api/v1/intents", response_model=IntentResponse)
@require_rate_limit
async def submit_intent(
    request: Request,
    intent_request: IntentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Submit natural language intent for execution

    Requires:
    - Authentication (JWT token)
    - Active subscription or trial
    - Rate limiting based on tier

    Args:
        request: FastAPI request object
        intent_request: Intent request
        credentials: JWT credentials

    Returns:
        Intent submission response with workflow ID
    """
    # Get authenticated user
    user = AuthMiddleware.get_current_user(credentials)
    user_id = user["user_id"]

    logger.info(
        f"Received intent submission",
        user_id=user_id,
        intent=intent_request.intent[:100],
    )

    try:
        # Check trial status and deduct credits if on trial
        trial_status = stripe_service.check_trial_status(user_id)
        subscription = stripe_service.get_subscription(user_id)

        if trial_status and trial_status.get("is_active"):
            # Check if trial has credits
            if trial_status.get("credits_remaining", 0) <= 0:
                raise HTTPException(
                    status_code=403,
                    detail="Trial credits exhausted. Please upgrade to continue."
                )

            # Deduct 1 credit
            stripe_service.deduct_trial_credit(user_id)
            logger.info(f"Trial credit deducted", user_id=user_id)

        elif not subscription or subscription.get("status") != "active":
            raise HTTPException(
                status_code=402,
                detail="Active subscription required. Please upgrade to continue."
            )

        # Create workflow in session memory
        workflow_id = session_memory.create_workflow(
            user_id=user_id,
            intent=intent_request.intent,
            goal_graph={},  # Will be populated by intent processor
        )

        # Publish intent submitted event
        event_bus.publish(
            "intent.submitted",
            {
                "workflow_id": workflow_id,
                "user_id": user_id,
                "intent": intent_request.intent,
                "context": intent_request.context,
            },
        )

        # Estimate cost and time (simplified)
        estimated_cost = 0.15
        estimated_time = 45.0

        logger.info(f"Intent submitted successfully", workflow_id=workflow_id)

        # Return trial status in response
        response_data = IntentResponse(
            workflow_id=workflow_id,
            status="pending",
            estimated_cost=estimated_cost,
            estimated_time=estimated_time,
            message="Intent submitted successfully. Workflow is being processed.",
        )

        # Add trial info to response if applicable
        if trial_status and trial_status.get("is_active"):
            response_data.message += f" Trial credits remaining: {trial_status.get('credits_remaining', 0)}"

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit intent", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to submit intent: {str(e)}")


@app.get("/api/v1/workflows/{workflow_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    workflow_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Get workflow execution status

    Args:
        workflow_id: Workflow ID
        credentials: JWT credentials

    Returns:
        Workflow status
    """
    # Get authenticated user
    user = AuthMiddleware.get_current_user(credentials)
    user_id = user["user_id"]

    try:
        workflow = session_memory.get_workflow(workflow_id)

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        # Verify user owns workflow
        if workflow["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        return WorkflowStatusResponse(
            workflow_id=workflow_id,
            status=workflow["status"],
            created_at=workflow["created_at"],
            completed_at=workflow.get("completed_at"),
            cost=workflow.get("cost", 0.0),
            confidence=workflow.get("confidence"),
            steps_completed=0,  # Will be tracked properly
            steps_failed=0,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow status", error=str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to get workflow status: {str(e)}"
        )


@app.get("/api/v1/workflows/{workflow_id}/audit", response_model=AuditTrailResponse)
async def get_audit_trail(
    workflow_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Get complete audit trail for workflow

    Args:
        workflow_id: Workflow ID
        credentials: JWT credentials

    Returns:
        Audit trail
    """
    # Get authenticated user
    user = AuthMiddleware.get_current_user(credentials)
    user_id = user["user_id"]

    try:
        # Verify workflow exists and user owns it
        workflow = session_memory.get_workflow(workflow_id)

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        if workflow["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Get audit trail
        audit_entries = session_memory.get_audit_trail(workflow_id)

        return AuditTrailResponse(
            workflow_id=workflow_id,
            entries=audit_entries,
            total_entries=len(audit_entries),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get audit trail", error=str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to get audit trail: {str(e)}"
        )


@app.delete("/api/v1/workflows/{workflow_id}")
async def cancel_workflow(
    workflow_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Cancel running workflow

    Args:
        workflow_id: Workflow ID
        credentials: JWT credentials

    Returns:
        Cancellation confirmation
    """
    # Get authenticated user
    user = AuthMiddleware.get_current_user(credentials)
    user_id = user["user_id"]

    try:
        # Verify workflow exists and user owns it
        workflow = session_memory.get_workflow(workflow_id)

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        if workflow["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Update workflow status
        session_memory.update_workflow_status(workflow_id, "cancelled")

        # Publish event
        event_bus.publish(
            "workflow.cancelled",
            {"workflow_id": workflow_id, "user_id": user_id},
        )

        logger.info(f"Workflow cancelled", workflow_id=workflow_id)

        return {"message": "Workflow cancelled successfully", "workflow_id": workflow_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel workflow", error=str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to cancel workflow: {str(e)}"
        )


@app.post("/api/v1/workflows/{workflow_id}/resume")
async def resume_workflow(
    workflow_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Resume paused workflow

    Args:
        workflow_id: Workflow ID
        credentials: JWT credentials

    Returns:
        Resume confirmation
    """
    # Get authenticated user
    user = AuthMiddleware.get_current_user(credentials)
    user_id = user["user_id"]

    try:
        # Verify workflow exists and user owns it
        workflow = session_memory.get_workflow(workflow_id)

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        if workflow["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Publish resume event
        event_bus.publish(
            "workflow.resume_requested",
            {"workflow_id": workflow_id, "user_id": user_id},
        )

        logger.info(f"Workflow resume requested", workflow_id=workflow_id)

        return {"message": "Workflow resume requested", "workflow_id": workflow_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resume workflow", error=str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to resume workflow: {str(e)}"
        )


# ============================================================================
# Startup/Shutdown
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global session_memory, working_memory, event_bus, stripe_service

    logger.info("Starting AUTOOS API server")

    # Initialize components
    database_url = (
        f"postgresql://{os.getenv('POSTGRES_USER', 'autoos')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'autoos_password')}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'autoos')}"
    )

    session_memory = SessionMemory(database_url)

    working_memory = WorkingMemory(
        redis_host=os.getenv("REDIS_HOST", "localhost"),
        redis_port=int(os.getenv("REDIS_PORT", "6379")),
        redis_db=int(os.getenv("REDIS_DB", "0")),
        redis_password=os.getenv("REDIS_PASSWORD"),
    )

    event_bus = EventBus(
        redis_host=os.getenv("REDIS_HOST", "localhost"),
        redis_port=int(os.getenv("REDIS_PORT", "6379")),
        redis_db=int(os.getenv("REDIS_DB", "0")),
        redis_password=os.getenv("REDIS_PASSWORD"),
    )

    # Initialize Stripe service
    stripe_service = StripeService()

    logger.info("AUTOOS API server started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AUTOOS API server")

    if session_memory:
        session_memory.close()

    if working_memory:
        working_memory.close()

    if event_bus:
        event_bus.close()

    logger.info("AUTOOS API server shutdown complete")


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception", error=str(exc), path=request.url.path)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
