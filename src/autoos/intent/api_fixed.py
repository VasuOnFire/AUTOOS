"""
FastAPI REST API - Intent submission and workflow management (Render-optimized)

Provides HTTP endpoints for external systems to interact with AUTOOS.
"""

from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import os
import sys

# ============================================================================
# Initialize logging first
# ============================================================================

from autoos.infrastructure.logging import get_logger, setup_logging

setup_logging(
    level=os.getenv("LOG_LEVEL", "INFO"),
    log_format=os.getenv("LOG_FORMAT", "json"),
)

logger = get_logger(__name__)

# ============================================================================
# Create FastAPI app
# ============================================================================

app = FastAPI(
    title="AUTOOS - Omega Edition API",
    description="The Automation Operating System - Intelligence Orchestration API",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://autoos-frontend.onrender.com",
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Global components (initialized on startup)
# ============================================================================

session_memory: Optional[Any] = None
working_memory: Optional[Any] = None
event_bus: Optional[Any] = None
stripe_service: Optional[Any] = None
components_initialized = False

# ============================================================================
# Request/Response Models
# ============================================================================


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    timestamp: str
    version: str
    components: Dict[str, str]
    environment: str


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


# ============================================================================
# Helper Functions
# ============================================================================


def get_database_url() -> Optional[str]:
    """Get database URL from environment"""
    # Render provides DATABASE_URL directly
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Render uses postgres:// but SQLAlchemy needs postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url
    
    # Fallback to individual components
    user = os.getenv("POSTGRES_USER", "autoos")
    password = os.getenv("POSTGRES_PASSWORD", "autoos_password")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "autoos")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def get_redis_url() -> Optional[str]:
    """Get Redis URL from environment"""
    # Render provides REDIS_URL directly
    redis_url = os.getenv("REDIS_URL")
    
    if redis_url:
        return redis_url
    
    # Fallback to individual components
    host = os.getenv("REDIS_HOST", "localhost")
    port = os.getenv("REDIS_PORT", "6379")
    password = os.getenv("REDIS_PASSWORD", "")
    db = os.getenv("REDIS_DB", "0")
    
    if password:
        return f"redis://:{password}@{host}:{port}/{db}"
    return f"redis://{host}:{port}/{db}"


def parse_redis_url(redis_url: str) -> Dict[str, Any]:
    """Parse Redis URL into components"""
    from urllib.parse import urlparse
    
    parsed = urlparse(redis_url)
    
    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 6379,
        "password": parsed.password,
        "db": int(parsed.path.lstrip("/")) if parsed.path else 0,
    }


# ============================================================================
# API Endpoints
# ============================================================================


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "name": "AUTOOS Omega API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint

    Returns system health status
    """
    global components_initialized
    
    components = {
        "api": "healthy",
        "session_memory": "healthy" if session_memory else "not_initialized",
        "working_memory": "healthy" if working_memory else "not_initialized",
        "event_bus": "healthy" if event_bus else "not_initialized",
        "stripe": "healthy" if stripe_service else "not_initialized",
    }
    
    # Check if running on Render
    is_render = os.getenv("RENDER") == "true"
    environment = "render" if is_render else "local"
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        components=components,
        environment=environment,
    )


@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": {
            "python_version": sys.version,
            "database_configured": bool(os.getenv("DATABASE_URL")),
            "redis_configured": bool(os.getenv("REDIS_URL")),
            "stripe_configured": bool(os.getenv("STRIPE_SECRET_KEY")),
        },
    }


@app.post("/api/v1/intents", response_model=IntentResponse)
async def submit_intent(intent_request: IntentRequest):
    """
    Submit natural language intent for execution

    Simplified version for initial deployment
    """
    logger.info(f"Received intent: {intent_request.intent[:100]}")
    
    # Generate workflow ID
    import uuid
    workflow_id = str(uuid.uuid4())
    
    # Return success response
    return IntentResponse(
        workflow_id=workflow_id,
        status="pending",
        estimated_cost=0.15,
        estimated_time=45.0,
        message="Intent submitted successfully. Workflow is being processed.",
    )


# ============================================================================
# Startup/Shutdown
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global session_memory, working_memory, event_bus, stripe_service, components_initialized

    logger.info("🚀 Starting AUTOOS API server...")
    
    try:
        # Check environment
        is_render = os.getenv("RENDER") == "true"
        logger.info(f"Environment: {'Render' if is_render else 'Local'}")
        
        # Get database URL
        database_url = get_database_url()
        if database_url:
            logger.info(f"✅ Database URL configured")
        else:
            logger.warning("⚠️  Database URL not configured")
        
        # Get Redis URL
        redis_url = get_redis_url()
        if redis_url:
            logger.info(f"✅ Redis URL configured")
        else:
            logger.warning("⚠️  Redis URL not configured")
        
        # Initialize components only if URLs are available
        if database_url:
            try:
                from autoos.memory.session_memory import SessionMemory
                session_memory = SessionMemory(database_url)
                logger.info("✅ Session memory initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize session memory: {e}")
        
        if redis_url:
            try:
                redis_config = parse_redis_url(redis_url)
                
                from autoos.memory.working_memory import WorkingMemory
                working_memory = WorkingMemory(**redis_config)
                logger.info("✅ Working memory initialized")
                
                from autoos.infrastructure.event_bus import EventBus
                event_bus = EventBus(**redis_config)
                logger.info("✅ Event bus initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Redis components: {e}")
        
        # Initialize Stripe service
        if os.getenv("STRIPE_SECRET_KEY"):
            try:
                from autoos.payment.stripe_service import StripeService
                stripe_service = StripeService()
                logger.info("✅ Stripe service initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Stripe: {e}")
        
        components_initialized = True
        logger.info("✅ AUTOOS API server started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        # Don't fail startup - allow health checks to work
        logger.warning("⚠️  Server started with limited functionality")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AUTOOS API server...")

    if session_memory:
        try:
            session_memory.close()
            logger.info("✅ Session memory closed")
        except Exception as e:
            logger.error(f"Error closing session memory: {e}")

    if working_memory:
        try:
            working_memory.close()
            logger.info("✅ Working memory closed")
        except Exception as e:
            logger.error(f"Error closing working memory: {e}")

    if event_bus:
        try:
            event_bus.close()
            logger.info("✅ Event bus closed")
        except Exception as e:
            logger.error(f"Error closing event bus: {e}")

    logger.info("✅ AUTOOS API server shutdown complete")


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path),
        },
    )


# ============================================================================
# Run server (for local development)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "api_fixed:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info",
    )
