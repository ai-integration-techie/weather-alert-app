from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime
from python_src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class RootAgent(BaseAgent):
    """Primary orchestrator for weather insights and emergency response queries"""
    
    def __init__(self):
        super().__init__(
            name='root-agent',
            description='Primary orchestrator for weather insights and emergency response queries'
        )
        self.capabilities = [
            'user_interaction',
            'query_interpretation', 
            'agent_coordination',
            'response_synthesis'
        ]
    
    async def _setup_tools(self):
        """Setup Root Agent specific tools"""
        self.tools = [
            {
                'name': 'coordinate_agents',
                'description': 'Coordinate with specialized agents for complex queries',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'query': {'type': 'string'},
                        'agents_needed': {'type': 'array', 'items': {'type': 'string'}},
                        'priority': {'type': 'string', 'enum': ['low', 'medium', 'high', 'emergency']}
                    }
                }
            },
            {
                'name': 'synthesize_response',
                'description': 'Combine responses from multiple agents into coherent answer',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'agent_responses': {'type': 'array'},
                        'context': {'type': 'object'}
                    }
                }
            }
        ]
    
    async def process_request(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process user query and coordinate with other agents"""
        try:
            query_analysis = await self.analyze_query(query)
            required_agents = self.determine_required_agents(query_analysis)
            
            # Get orchestrator from context to coordinate agents
            orchestrator = context.get('orchestrator')
            if orchestrator and required_agents:
                agent_responses = await orchestrator.coordinate_agents(
                    required_agents, query, context
                )
            else:
                agent_responses = []
            
            response = await self.synthesize_response(agent_responses, query_analysis, context)
            return self.generate_success_response(response, context.get('request_id'))
            
        except Exception as e:
            logger.error(f"Root Agent error: {str(e)}")
            return self.generate_error_response(e, context.get('request_id'))
    
    async def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze user query to determine intent and requirements"""
        keywords = {
            'data': ['historical', 'records', 'statistics', 'data', 'trends'],
            'forecast': ['forecast', 'prediction', 'upcoming', 'future', 'expected'],
            'emergency': ['hurricane', 'tornado', 'flood', 'evacuation', 'emergency', 'disaster'],
            'location': ['city', 'county', 'state', 'zip', 'coordinates', 'area']
        }
        
        analysis = {
            'type': 'general',
            'urgency': 'medium',
            'location_based': False,
            'time_sensitive': False
        }
        
        query_lower = query.lower()
        
        if any(word in query_lower for word in keywords['emergency']):
            analysis['urgency'] = 'high'
            analysis['type'] = 'emergency'
        
        if any(word in query_lower for word in keywords['forecast']):
            analysis['type'] = 'forecast'
            analysis['time_sensitive'] = True
        
        if any(word in query_lower for word in keywords['data']):
            analysis['type'] = 'data_analysis'
        
        if any(word in query_lower for word in keywords['location']):
            analysis['location_based'] = True
        
        return analysis
    
    def determine_required_agents(self, analysis: Dict[str, Any]) -> List[str]:
        """Determine which agents are needed based on query analysis"""
        agents = []
        
        if analysis['type'] == 'emergency':
            agents.extend(['forecast', 'data', 'insights'])
        elif analysis['type'] == 'forecast':
            agents.append('forecast')
            if analysis['location_based']:
                agents.append('data')
        elif analysis['type'] == 'data_analysis':
            agents.extend(['data', 'insights'])
        else:
            agents.append('forecast')
        
        return agents
    
    async def synthesize_response(self, agent_responses: List[Dict], analysis: Dict, context: Dict) -> Dict[str, Any]:
        """Synthesize responses from multiple agents into coherent answer"""
        synthesis = {
            'summary': '',
            'details': [],
            'recommendations': [],
            'urgency': analysis['urgency'],
            'timestamp': datetime.utcnow().isoformat(),
            'sources': []
        }
        
        for response in agent_responses:
            if 'response' in response and response['response'].get('success'):
                data = response['response']['data']
                
                if 'summary' in data:
                    synthesis['summary'] += data['summary'] + ' '
                if 'details' in data:
                    if isinstance(data['details'], list):
                        synthesis['details'].extend(data['details'])
                    else:
                        synthesis['details'].append(data['details'])
                if 'recommendations' in data:
                    synthesis['recommendations'].extend(data['recommendations'])
                if 'sources' in data:
                    synthesis['sources'].extend(data['sources'])
        
        if analysis['urgency'] == 'high':
            synthesis['alert'] = True
            synthesis['immediate_actions'] = self.generate_emergency_actions(agent_responses)
        
        return synthesis
    
    def generate_emergency_actions(self, responses: List[Dict]) -> List[str]:
        """Generate emergency actions based on agent responses"""
        actions = []
        
        for response in responses:
            if 'response' in response and response['response'].get('success'):
                data = response['response']['data']
                if 'emergency_actions' in data:
                    actions.extend(data['emergency_actions'])
        
        return actions if actions else [
            'Monitor weather conditions closely',
            'Review emergency preparedness plans', 
            'Stay informed through official channels'
        ]