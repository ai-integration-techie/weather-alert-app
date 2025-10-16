import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from python_src.agents.root_agent import RootAgent
from python_src.agents.data_agent import DataAgent
from python_src.agents.forecast_agent import ForecastAgent
from python_src.agents.insights_agent import InsightsAgent
from python_src.config.environment import config

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Orchestrates multiple weather insight agents for coordinated responses"""
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.request_history: List[Dict[str, Any]] = []
        self.active_requests: Dict[str, Dict[str, Any]] = {}
        
        self.agent_types = {
            'root': RootAgent,
            'data': DataAgent,
            'forecast': ForecastAgent,
            'insights': InsightsAgent
        }
        
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize all agents in the orchestrator"""
        try:
            logger.info('Initializing Agent Orchestrator...')
            
            for agent_type, agent_class in self.agent_types.items():
                logger.info(f'Initializing {agent_type} agent...')
                agent = agent_class()
                await agent.initialize()
                self.agents[agent_type] = agent
                logger.info(f'{agent_type} agent initialized successfully')
            
            self.initialized = True
            logger.info('Agent Orchestrator initialization complete')
            return True
            
        except Exception as e:
            logger.error(f'Failed to initialize Agent Orchestrator: {str(e)}')
            raise
    
    async def process_user_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a user query through the agent system"""
        if not self.initialized:
            raise RuntimeError("Agent Orchestrator not initialized")
        
        request_id = self._generate_request_id()
        start_time = datetime.utcnow()
        
        if context is None:
            context = {}
        
        try:
            logger.info(f"Processing query [{request_id}]: {query[:100]}...")
            
            # Track active request
            self.active_requests[request_id] = {
                'query': query,
                'context': context,
                'start_time': start_time,
                'status': 'processing'
            }
            
            # Process through root agent
            root_agent = self.agents['root']
            response = await root_agent.process_request(query, {
                **context,
                'request_id': request_id,
                'orchestrator': self
            })
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds() * 1000  # milliseconds
            
            # Update request tracking
            self.active_requests[request_id].update({
                'status': 'completed',
                'duration': duration,
                'response': response
            })
            
            # Add to history
            self.request_history.append({
                'request_id': request_id,
                'query': query,
                'response': response,
                'duration': duration,
                'timestamp': start_time.isoformat()
            })
            
            logger.info(f"Query processed [{request_id}] in {duration:.0f}ms")
            return self._format_response(response, request_id)
            
        except Exception as e:
            logger.error(f"Error processing query [{request_id}]: {str(e)}")
            
            # Update request with error
            self.active_requests[request_id].update({
                'status': 'error',
                'error': str(e)
            })
            
            return self._format_error_response(e, request_id)
    
    async def coordinate_agents(self, agent_types: List[str], query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Coordinate multiple agents for complex queries"""
        coordination_id = self._generate_request_id()
        logger.info(f"Coordinating agents [{coordination_id}]: {', '.join(agent_types)}")
        
        try:
            # Create tasks for parallel execution
            tasks = []
            for agent_type in agent_types:
                if agent_type not in self.agents:
                    logger.warning(f"Agent type '{agent_type}' not found, skipping")
                    continue
                
                agent = self.agents[agent_type]
                task = self._call_agent_async(agent, agent_type, query, {
                    **context,
                    'coordination_id': coordination_id
                })
                tasks.append(task)
            
            # Execute all agent calls in parallel
            agent_responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process responses and handle exceptions
            processed_responses = []
            for i, response in enumerate(agent_responses):
                if isinstance(response, Exception):
                    logger.error(f"Agent {agent_types[i]} failed: {str(response)}")
                    processed_responses.append({
                        'agent_type': agent_types[i],
                        'response': {'error': True, 'message': str(response)},
                        'timestamp': datetime.utcnow().isoformat()
                    })
                else:
                    processed_responses.append(response)
            
            logger.info(f"Agent coordination [{coordination_id}] completed")
            return processed_responses
            
        except Exception as e:
            logger.error(f"Agent coordination [{coordination_id}] failed: {str(e)}")
            raise
    
    async def _call_agent_async(self, agent: Any, agent_type: str, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Async wrapper for agent calls"""
        logger.debug(f"Calling {agent_type} agent...")
        
        try:
            response = await agent.process_request(query, context)
            return {
                'agent_type': agent_type,
                'response': response,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error calling {agent_type} agent: {str(e)}")
            raise
    
    async def handle_emergency_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle emergency queries with priority processing"""
        logger.warning('EMERGENCY QUERY DETECTED - Prioritizing response')
        
        if context is None:
            context = {}
        
        emergency_context = {
            **context,
            'priority': 'emergency',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Coordinate all agents for emergency analysis
        required_agents = ['forecast', 'data', 'insights']
        agent_responses = await self.coordinate_agents(required_agents, query, emergency_context)
        
        # Get insights agent for emergency correlation
        insights_agent = self.agents['insights']
        emergency_analysis = await insights_agent.process_request(query, {
            **emergency_context,
            'agent_responses': agent_responses,
            'analysis_type': 'emergency_correlation'
        })
        
        return {
            'type': 'emergency_response',
            'analysis': emergency_analysis,
            'agent_responses': agent_responses,
            'timestamp': datetime.utcnow().isoformat(),
            'priority': 'critical'
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents and orchestrator"""
        status = {
            'orchestrator': {
                'initialized': self.initialized,
                'active_requests': len(self.active_requests),
                'total_requests': len(self.request_history)
            },
            'agents': {}
        }
        
        for agent_type, agent in self.agents.items():
            status['agents'][agent_type] = {
                'name': agent.name,
                'capabilities': getattr(agent, 'capabilities', []),
                'initialized': getattr(agent, 'initialized', False)
            }
        
        return status
    
    def get_request_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent request history"""
        return [
            {
                'request_id': req['request_id'],
                'query': req['query'][:100] + ('...' if len(req['query']) > 100 else ''),
                'duration': req['duration'],
                'timestamp': req['timestamp']
            }
            for req in self.request_history[-limit:]
        ]
    
    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get capabilities of all agents"""
        capabilities = {}
        
        for agent_type, agent in self.agents.items():
            capabilities[agent_type] = {
                'name': agent.name,
                'description': getattr(agent, 'description', f'{agent_type} agent for weather insights'),
                'capabilities': getattr(agent, 'capabilities', []),
                'tools': [
                    {
                        'name': tool.get('name', 'Unknown'),
                        'description': tool.get('description', 'No description')
                    }
                    for tool in getattr(agent, 'tools', [])
                ]
            }
        
        return capabilities
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all agents"""
        health = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'agents': {},
            'system': {
                'active_requests': len(self.active_requests),
                'initialized': self.initialized
            }
        }
        
        for agent_type, agent in self.agents.items():
            try:
                health['agents'][agent_type] = {
                    'status': 'healthy',
                    'initialized': getattr(agent, 'initialized', False),
                    'capabilities': len(getattr(agent, 'capabilities', []))
                }
            except Exception as e:
                health['agents'][agent_type] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health['status'] = 'degraded'
        
        return health
    
    async def shutdown(self):
        """Shutdown all agents and cleanup resources"""
        logger.info('Shutting down Agent Orchestrator...')
        
        for agent_type, agent in self.agents.items():
            try:
                await agent.shutdown()
                logger.info(f'{agent_type} agent shut down successfully')
            except Exception as e:
                logger.error(f'Error shutting down {agent_type} agent: {str(e)}')
        
        self.agents.clear()
        self.active_requests.clear()
        self.initialized = False
        logger.info('Agent Orchestrator shutdown complete')
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        random_part = str(uuid.uuid4())[:8]
        return f"req_{timestamp}_{random_part}"
    
    def _format_response(self, response: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Format successful response"""
        return {
            'request_id': request_id,
            'status': 'success',
            'data': response,
            'timestamp': datetime.utcnow().isoformat(),
            'agent_system': 'Weather Insights Advisor'
        }
    
    def _format_error_response(self, error: Exception, request_id: str) -> Dict[str, Any]:
        """Format error response"""
        return {
            'request_id': request_id,
            'status': 'error',
            'error': {
                'message': str(error),
                'type': type(error).__name__
            },
            'timestamp': datetime.utcnow().isoformat(),
            'agent_system': 'Weather Insights Advisor'
        }