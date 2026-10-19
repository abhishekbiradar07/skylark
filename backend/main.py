"""
FastAPI Backend for Skylark Drones BI Agent
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Skylark Drones BI Agent API",
    description="Business Intelligence Agent for Monday.com data",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    metrics: List[Dict[str, Any]] = []
    insights: List[str] = []
    data_quality: List[str] = []
    charts: List[Dict[str, Any]] = []


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Skylark Drones BI Agent",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Skylark Drones BI Agent API",
        "docs": "/docs",
        "health": "/health"
    }


# Import agent
import sys
sys.path.insert(0, os.path.dirname(__file__))
from agent.agent import agent


# Chat endpoint
@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint for conversational queries using AI Agent
    """
    logger.info(f"Received chat request: {request.message}")
    
    try:
        # Process query through agent
        result = await agent.process_query(
            user_message=request.message,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(
            answer=result["answer"],
            metrics=result.get("metrics", []),
            insights=result.get("insights", []),
            data_quality=result.get("data_quality", []),
            charts=result.get("charts", [])
        )
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return ChatResponse(
            answer=f"I encountered an error processing your request: {str(e)}",
            insights=[],
            data_quality=["Error occurred during processing"]
        )


# Dashboard endpoints (placeholders)
@app.get("/api/dashboard/overview")
async def get_overview():
    """Get overview dashboard data"""
    return {
        "status": "success",
        "message": "Overview endpoint - implementation in progress"
    }


@app.get("/api/dashboard/pipeline")
async def get_pipeline():
    """Get pipeline dashboard data"""
    return {
        "status": "success",
        "message": "Pipeline endpoint - implementation in progress"
    }


@app.get("/api/dashboard/operations")
async def get_operations():
    """Get operations dashboard data"""
    return {
        "status": "success",
        "message": "Operations endpoint - implementation in progress"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
