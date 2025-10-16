from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime
from python_src.config.environment import config

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all weather insight agents"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.project_id = config.PROJECT_ID
        self.region = config.AGENT_REGION
        self.capabilities: List[str] = []
        self.tools: List[Dict[str, Any]] = []
        self.initialized = False
        
    async def initialize(self) -> bool:
        """Initialize the agent"""
        try:
            logger.info(f"Initializing {self.name}...")
            await self._setup_tools()
            self.initialized = True
            logger.info(f"{self.name} initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize {self.name}: {str(e)}")
            raise
    
    @abstractmethod
    async def _setup_tools(self):
        """Setup agent-specific tools"""
        pass
    
    @abstractmethod
    async def process_request(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request and return response"""
        pass
    
    def classify_query(self, query: str) -> str:
        """Classify the type of query"""
        query_lower = query.lower()
        
        # Common classification logic that can be overridden
        if any(word in query_lower for word in ['emergency', 'urgent', 'immediate']):
            return 'emergency'
        elif any(word in query_lower for word in ['forecast', 'prediction', 'future']):
            return 'forecast'
        elif any(word in query_lower for word in ['historical', 'data', 'records']):
            return 'historical'
        else:
            return 'general'
    
    def generate_error_response(self, error: Exception, request_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate standardized error response"""
        return {
            'error': True,
            'message': f'{self.name} encountered an error: {str(error)}',
            'agent': self.name,
            'request_id': request_id,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def generate_success_response(self, data: Dict[str, Any], request_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate standardized success response"""
        return {
            'success': True,
            'agent': self.name,
            'data': data,
            'request_id': request_id,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def shutdown(self):
        """Cleanup agent resources"""
        logger.info(f"Shutting down {self.name}...")
        self.initialized = False