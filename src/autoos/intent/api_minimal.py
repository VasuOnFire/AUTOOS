"""
Minimal API for AUTOOS Omega - Works without external dependencies
This version runs even if database/redis are not available
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="AUTOOS Omega API",
    description="Automation Operating System - Minimal Version",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage (for demo purposes)
workflows = {}
workflow_counter = 0

# Models
class IntentRequest(BaseModel):
    intent: str
    user_id: str = "demo-user"

class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    intent: str
    created_at: str
    message: str

# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "service": "AUTOOS Omega API",
        "version": "1.0.0",
        "message": "Welcome to AUTOOS Omega - Automation Operating System",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "running",
            "database": "optional",
            "redis": "optional"
        }
    }

@app.post("/intents", response_model=WorkflowResponse)
async def submit_intent(request: IntentRequest):
    """
    Submit a natural language intent for processing
    
    This is a minimal version that works without database/redis
    """
    global workflow_counter
    workflow_counter += 1
    
    workflow_id = f"wf-{workflow_counter:06d}"
    
    # Store in memory
    workflow = {
        "workflow_id": workflow_id,
        "status": "processing",
        "intent": request.intent,
        "user_id": request.user_id,
        "created_at": datetime.utcnow().isoformat(),
        "message": "Intent received and queued for processing"
    }
    
    workflows[workflow_id] = workflow
    
    return WorkflowResponse(**workflow)

@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow status by ID"""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return workflows[workflow_id]

@app.get("/workflows")
async def list_workflows(user_id: str = "demo-user", limit: int = 10):
    """List workflows for a user"""
    user_workflows = [
        w for w in workflows.values() 
        if w.get("user_id") == user_id
    ]
    
    return {
        "workflows": user_workflows[:limit],
        "total": len(user_workflows)
    }

@app.delete("/workflows/{workflow_id}")
async def cancel_workflow(workflow_id: str):
    """Cancel a workflow"""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflows[workflow_id]["status"] = "cancelled"
    
    return {
        "message": "Workflow cancelled successfully",
        "workflow_id": workflow_id
    }

@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    return {
        "total_workflows": len(workflows),
        "active_workflows": sum(1 for w in workflows.values() if w["status"] == "processing"),
        "completed_workflows": sum(1 for w in workflows.values() if w["status"] == "completed"),
        "cancelled_workflows": sum(1 for w in workflows.values() if w["status"] == "cancelled"),
        "timestamp": datetime.utcnow().isoformat()
    }

# Authentication endpoints (minimal)
@app.post("/auth/signup")
async def signup():
    """Minimal signup endpoint"""
    return {
        "message": "Signup successful",
        "user_id": "demo-user",
        "token": "demo-token-12345"
    }

@app.post("/auth/signin")
async def signin():
    """Minimal signin endpoint"""
    return {
        "message": "Signin successful",
        "user_id": "demo-user",
        "token": "demo-token-12345"
    }

@app.get("/auth/me")
async def get_current_user():
    """Get current user info"""
    return {
        "user_id": "demo-user",
        "email": "demo@autoos.ai",
        "username": "demo",
        "role": "user"
    }

# Payment endpoints (minimal)
@app.get("/payments/pricing")
async def get_pricing():
    """Get pricing tiers"""
    return {
        "tiers": [
            {
                "name": "Free Trial",
                "price": 0,
                "duration": "30 days",
                "features": ["10 workflows/month", "2 concurrent agents"]
            },
            {
                "name": "Student",
                "price": 9.99,
                "features": ["100 workflows/month", "5 concurrent agents"]
            },
            {
                "name": "Professional",
                "price": 29.99,
                "features": ["Unlimited workflows", "20 concurrent agents"]
            }
        ]
    }

@app.post("/payments/start-trial")
async def start_trial():
    """Start free trial"""
    return {
        "message": "Free trial activated",
        "trial_end_date": "2024-03-15",
        "credits_remaining": 10
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
