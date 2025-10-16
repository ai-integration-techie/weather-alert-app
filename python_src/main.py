import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from python_src.orchestrator.agent_orchestrator import AgentOrchestrator
from python_src.config.environment import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator: Optional[AgentOrchestrator] = None

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str = Field(..., description="The weather query to process")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for the query")

class EmergencyRequest(BaseModel):
    query: str = Field(..., description="The emergency weather query")
    location: Optional[Dict[str, float]] = Field(default=None, description="Location coordinates")
    severity: Optional[str] = Field(default="high", description="Severity level")

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    agents: Dict[str, Any]
    system: Dict[str, Any]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown"""
    global orchestrator
    
    # Startup
    logger.info("Starting Weather Insights Advisor...")
    try:
        config.validate_config()
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        logger.info("Agent orchestrator initialized successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)
    
    # Shutdown
    logger.info("Shutting down Weather Insights Advisor...")
    if orchestrator:
        await orchestrator.shutdown()
    logger.info("Application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Weather Insights & Forecast Advisor",
    description="Multi-agent system for weather disaster relief and preparedness using Google ADK",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests"""
    start_time = asyncio.get_event_loop().time()
    logger.info(f"{request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = asyncio.get_event_loop().time() - start_time
    logger.info(f"Request completed in {process_time:.3f}s - Status: {response.status_code}")
    
    return response

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status": "error",
            "timestamp": "2024-01-01T00:00:00Z"  # Would use datetime.utcnow().isoformat() in real app
        }
    )

# Routes
@app.get("/", response_model=Dict[str, Any])
async def root():
    """Service information endpoint"""
    return {
        "name": "Weather Insights & Forecast Advisor",
        "description": "Multi-agent system for weather disaster relief and preparedness",
        "version": "1.0.0",
        "language": "Python",
        "framework": "FastAPI",
        "agents": ["Root Agent", "Data Agent", "Forecast Agent", "Insights Agent"],
        "capabilities": [
            "Weather disaster relief intelligence",
            "Emergency preparedness analysis", 
            "Historical weather data correlation",
            "Real-time forecast integration",
            "Risk assessment and insights"
        ]
    }

@app.post("/api/query", response_model=Dict[str, Any])
async def process_query(request: QueryRequest):
    """Process weather query through agent system"""
    global orchestrator
    
    if not orchestrator or not orchestrator.initialized:
        raise HTTPException(status_code=503, detail="Agent system not available")
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        response = await orchestrator.process_user_query(
            request.query,
            request.context or {}
        )
        return response
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process query")

@app.post("/api/emergency", response_model=Dict[str, Any]) 
async def process_emergency(request: EmergencyRequest):
    """Process emergency weather query with priority handling"""
    global orchestrator
    
    if not orchestrator or not orchestrator.initialized:
        raise HTTPException(status_code=503, detail="Agent system not available")
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Emergency query cannot be empty")
    
    try:
        emergency_context = {
            "priority": "emergency",
            "location": request.location,
            "severity": request.severity or "high"
        }
        
        response = await orchestrator.handle_emergency_query(
            request.query,
            emergency_context
        )
        
        return {
            "status": "success",
            "type": "emergency_response", 
            "data": response
        }
    except Exception as e:
        logger.error(f"Emergency query processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process emergency query")

@app.get("/api/status", response_model=Dict[str, Any])
async def get_status():
    """Get agent system status"""
    global orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Agent system not initialized")
    
    try:
        status = orchestrator.get_agent_status()
        return {
            "status": "operational",
            **status
        }
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get system status")

@app.get("/api/capabilities", response_model=Dict[str, Any])
async def get_capabilities():
    """Get agent capabilities"""
    global orchestrator
    
    if not orchestrator or not orchestrator.initialized:
        raise HTTPException(status_code=503, detail="Agent system not available")
    
    try:
        capabilities = await orchestrator.get_agent_capabilities()
        return {
            "status": "success",
            "capabilities": capabilities
        }
    except Exception as e:
        logger.error(f"Capabilities check error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get agent capabilities")

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    global orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Agent system not initialized")
    
    try:
        health = await orchestrator.health_check()
        status_code = 200 if health["status"] == "healthy" else 503
        
        if status_code != 200:
            raise HTTPException(status_code=status_code, detail="System unhealthy")
        
        return health
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        raise HTTPException(status_code=503, detail="Health check failed")

@app.get("/api/history", response_model=Dict[str, Any])
async def get_history(limit: int = 10):
    """Get request history"""
    global orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Agent system not initialized")
    
    try:
        history = orchestrator.get_request_history(limit)
        return {
            "status": "success",
            "history": history
        }
    except Exception as e:
        logger.error(f"History retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")

# Additional endpoints for debugging/monitoring
@app.get("/api/agents/{agent_type}/status")
async def get_agent_status(agent_type: str):
    """Get status of specific agent"""
    global orchestrator
    
    if not orchestrator or not orchestrator.initialized:
        raise HTTPException(status_code=503, detail="Agent system not available")
    
    if agent_type not in orchestrator.agents:
        raise HTTPException(status_code=404, detail=f"Agent type '{agent_type}' not found")
    
    agent = orchestrator.agents[agent_type]
    return {
        "agent_type": agent_type,
        "name": agent.name,
        "initialized": getattr(agent, 'initialized', False),
        "capabilities": getattr(agent, 'capabilities', [])
    }

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    # FastAPI will handle the shutdown via lifespan context manager

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the server
    uvicorn.run(
        "python_src.main:app",
        host="0.0.0.0",
        port=config.PORT,
        log_level="info",
        access_log=True,
        reload=config.ENVIRONMENT == "development"
    )