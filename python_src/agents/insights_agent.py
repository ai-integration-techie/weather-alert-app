from typing import Dict, List, Any, Optional
import asyncio
import logging
import random
from datetime import datetime
from python_src.agents.base_agent import BaseAgent
from python_src.config.environment import config

logger = logging.getLogger(__name__)

class InsightsAgent(BaseAgent):
    """Correlates data and generates natural-language summaries for actionable weather intelligence"""
    
    def __init__(self):
        super().__init__(
            name='insights-agent',
            description='Correlates data and generates natural-language summaries for actionable weather intelligence'
        )
        self.capabilities = [
            'data_correlation',
            'risk_assessment',
            'trend_analysis',
            'emergency_prioritization',
            'natural_language_synthesis'
        ]
    
    async def _setup_tools(self):
        """Setup Insights Agent specific tools"""
        self.tools = [
            {
                'name': 'correlate_historical_forecast',
                'description': 'Correlate historical data with current forecasts for risk assessment',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'historical_data': {'type': 'object'},
                        'forecast_data': {'type': 'object'},
                        'location_context': {'type': 'object'}
                    }
                }
            },
            {
                'name': 'assess_population_risk',
                'description': 'Assess risk to vulnerable populations based on weather conditions',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'weather_conditions': {'type': 'object'},
                        'demographic_data': {'type': 'object'},
                        'infrastructure_data': {'type': 'object'}
                    }
                }
            },
            {
                'name': 'generate_emergency_summary',
                'description': 'Generate actionable emergency response summary',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'severity_level': {'type': 'string'},
                        'affected_areas': {'type': 'array'},
                        'time_sensitive': {'type': 'boolean'}
                    }
                }
            }
        ]
    
    async def process_request(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process insights analysis request"""
        try:
            analysis_type = self.determine_analysis_type(query, context)
            
            if analysis_type == 'emergency_correlation':
                response_data = await self.handle_emergency_correlation(query, context)
            elif analysis_type == 'risk_assessment':
                response_data = await self.handle_risk_assessment(query, context)
            elif analysis_type == 'trend_analysis':
                response_data = await self.handle_trend_analysis(query, context)
            elif analysis_type == 'vulnerability_analysis':
                response_data = await self.handle_vulnerability_analysis(query, context)
            else:
                response_data = await self.handle_general_insights(query, context)
            
            return self.generate_success_response(response_data, context.get('request_id'))
            
        except Exception as e:
            logger.error(f"Insights Agent error: {str(e)}")
            return self.generate_error_response(e, context.get('request_id'))
    
    def determine_analysis_type(self, query: str, context: Dict[str, Any]) -> str:
        """Determine the type of analysis needed"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['emergency', 'evacuation', 'immediate']):
            return 'emergency_correlation'
        elif any(word in query_lower for word in ['risk', 'probability', 'chance']):
            return 'risk_assessment'
        elif any(word in query_lower for word in ['trend', 'pattern', 'historical']):
            return 'trend_analysis'
        elif any(word in query_lower for word in ['population', 'elderly', 'vulnerable']):
            return 'vulnerability_analysis'
        else:
            return 'general_insights'
    
    async def handle_emergency_correlation(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle emergency correlation analysis"""
        correlation_data = await self.correlate_emergency_factors(context)
        priority_assessment = self.assess_emergency_priority(correlation_data)
        
        return {
            'summary': self.generate_emergency_summary(correlation_data, priority_assessment),
            'details': {
                'correlation_factors': correlation_data['factors'],
                'priority_level': priority_assessment['level'],
                'time_sensitivity': priority_assessment['timeframe'],
                'affected_areas': correlation_data['geographic_impact']
            },
            'recommendations': self.generate_emergency_recommendations(priority_assessment),
            'emergency_actions': self.generate_immediate_actions(priority_assessment),
            'sources': ['Multi-agent correlation analysis'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def handle_risk_assessment(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle risk assessment analysis"""
        risk_factors = await self.identify_risk_factors(context)
        risk_score = self.calculate_risk_score(risk_factors)
        mitigation_strategies = self.generate_mitigation_strategies(risk_factors)
        
        return {
            'summary': f"Risk assessment complete: {risk_score['level']} risk level identified",
            'details': {
                'risk_score': risk_score['score'],
                'risk_level': risk_score['level'],
                'primary_factors': risk_factors['primary'],
                'secondary_factors': risk_factors['secondary'],
                'confidence_level': risk_score['confidence']
            },
            'recommendations': mitigation_strategies,
            'timeline': self.generate_risk_timeline(risk_factors),
            'sources': ['Risk assessment correlation'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def handle_trend_analysis(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle trend analysis"""
        trend_data = await self.analyze_trends(context)
        patterns = self.identify_patterns(trend_data)
        projections = self.generate_projections(patterns)
        
        return {
            'summary': f"Trend analysis reveals {len(patterns)} significant patterns",
            'details': {
                'identified_trends': patterns,
                'statistical_confidence': trend_data['confidence'],
                'data_span': trend_data['timespan'],
                'anomalies': trend_data['anomalies']
            },
            'projections': projections,
            'insights': self.generate_trend_insights(patterns),
            'sources': ['Historical trend analysis'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def handle_vulnerability_analysis(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle vulnerability analysis"""
        vulnerability_factors = await self.assess_vulnerability_factors(context)
        population_impact = self.calculate_population_impact(vulnerability_factors)
        protection_strategies = self.generate_protection_strategies(vulnerability_factors)
        
        return {
            'summary': f"Vulnerability analysis identifies {len(population_impact['high_risk_groups'])} high-risk population groups",
            'details': {
                'vulnerability_score': vulnerability_factors['score'],
                'high_risk_groups': population_impact['high_risk_groups'],
                'geographic_factors': vulnerability_factors['geographic'],
                'infrastructure_factors': vulnerability_factors['infrastructure'],
                'social_factors': vulnerability_factors['social']
            },
            'recommendations': protection_strategies,
            'priority_actions': self.generate_priority_actions(population_impact),
            'sources': ['Vulnerability assessment'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def handle_general_insights(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general insights request"""
        return {
            'summary': 'General weather insights available',
            'details': {
                'capabilities': self.capabilities,
                'analysis_types': ['emergency_correlation', 'risk_assessment', 'trend_analysis', 'vulnerability_analysis']
            },
            'sources': ['Insights Agent'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def correlate_emergency_factors(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Correlate various emergency factors"""
        factors = {
            'weather_severity': self.assess_weather_severity(context),
            'historical_precedent': self.assess_historical_precedent(context),
            'population_density': self.assess_population_density(context),
            'infrastructure_vulnerability': self.assess_infrastructure_vulnerability(context),
            'response_capacity': self.assess_response_capacity(context)
        }
        
        geographic_impact = self.calculate_geographic_impact(factors)
        correlation_strength = self.calculate_correlation_strength(factors)
        
        return {
            'factors': factors,
            'geographic_impact': geographic_impact,
            'correlation_strength': correlation_strength
        }
    
    def assess_emergency_priority(self, correlation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the priority level of an emergency situation"""
        priority_score = 0
        factors = correlation_data['factors']
        
        # Weight different factors
        if factors['weather_severity'] >= 8:
            priority_score += 40
        elif factors['weather_severity'] >= 6:
            priority_score += 25
        elif factors['weather_severity'] >= 4:
            priority_score += 15
        
        if factors['historical_precedent'] >= 7:
            priority_score += 20
        if factors['population_density'] >= 7:
            priority_score += 15
        if factors['infrastructure_vulnerability'] >= 6:
            priority_score += 15
        if factors['response_capacity'] <= 4:
            priority_score += 10
        
        # Determine level and timeframe
        if priority_score >= 80:
            level = 'critical'
            timeframe = 'immediate'
        elif priority_score >= 60:
            level = 'high'
            timeframe = '2-6 hours'
        elif priority_score >= 40:
            level = 'medium'
            timeframe = '6-12 hours'
        else:
            level = 'low'
            timeframe = '24-48 hours'
        
        return {
            'level': level,
            'score': priority_score,
            'timeframe': timeframe
        }
    
    def generate_emergency_summary(self, correlation_data: Dict[str, Any], priority_assessment: Dict[str, Any]) -> str:
        """Generate emergency situation summary"""
        level = priority_assessment['level']
        timeframe = priority_assessment['timeframe']
        factors = [
            key for key, value in correlation_data['factors'].items()
            if value >= 6
        ]
        
        if level == 'critical':
            return f"CRITICAL: Immediate emergency response required within {timeframe}. Primary concerns: {', '.join(factors)}."
        elif level == 'high':
            return f"HIGH PRIORITY: Emergency preparations needed within {timeframe}. Key factors: {', '.join(factors)}."
        else:
            return f"Monitoring situation. Preparedness recommended within {timeframe}. Factors to watch: {', '.join(factors)}."
    
    def generate_emergency_recommendations(self, priority_assessment: Dict[str, Any]) -> List[str]:
        """Generate emergency recommendations based on priority"""
        recommendations = []
        
        if priority_assessment['level'] == 'critical':
            recommendations.extend([
                'Activate emergency operations center immediately',
                'Issue evacuation orders for high-risk areas',
                'Deploy emergency response teams'
            ])
        elif priority_assessment['level'] == 'high':
            recommendations.extend([
                'Place emergency services on standby',
                'Issue public safety advisories',
                'Prepare evacuation routes and shelters'
            ])
        else:
            recommendations.extend([
                'Monitor conditions closely',
                'Review emergency response plans',
                'Inform public of potential risks'
            ])
        
        return recommendations
    
    def generate_immediate_actions(self, priority_assessment: Dict[str, Any]) -> List[str]:
        """Generate immediate actions based on timeframe"""
        actions = []
        
        if priority_assessment['timeframe'] == 'immediate':
            actions.extend([
                'Execute emergency protocols NOW',
                'Notify all emergency personnel',
                'Begin public notifications'
            ])
        elif 'hours' in priority_assessment['timeframe']:
            actions.extend([
                'Alert emergency management teams',
                'Prepare public communication systems',
                'Stage emergency resources'
            ])
        
        return actions
    
    async def identify_risk_factors(self, context: Dict[str, Any]) -> Dict[str, List[str]]:
        """Identify primary and secondary risk factors"""
        return {
            'primary': [
                'Severe weather conditions forecasted',
                'Historical precedent for flooding in area',
                'High population density in affected zone'
            ],
            'secondary': [
                'Limited evacuation route capacity',
                'Aging infrastructure',
                'Tourist season population increase'
            ]
        }
    
    def calculate_risk_score(self, risk_factors: Dict[str, List[str]]) -> Dict[str, Any]:
        """Calculate overall risk score"""
        primary_weight = 0.7
        secondary_weight = 0.3
        
        primary_score = len(risk_factors['primary']) * 25
        secondary_score = len(risk_factors['secondary']) * 15
        
        total_score = (primary_score * primary_weight) + (secondary_score * secondary_weight)
        
        if total_score >= 70:
            level = 'high'
        elif total_score >= 40:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'score': round(total_score),
            'level': level,
            'confidence': 0.85
        }
    
    def generate_mitigation_strategies(self, risk_factors: Dict[str, List[str]]) -> List[str]:
        """Generate risk mitigation strategies"""
        strategies = []
        
        if any('flood' in factor.lower() for factor in risk_factors['primary']):
            strategies.extend([
                'Deploy water rescue teams to high-risk areas',
                'Open elevated emergency shelters'
            ])
        
        if any('infrastructure' in factor.lower() for factor in risk_factors['secondary']):
            strategies.extend([
                'Inspect critical infrastructure systems',
                'Prepare backup power systems'
            ])
        
        return strategies
    
    # Assessment utility methods (simplified for demo)
    def assess_weather_severity(self, context: Dict[str, Any]) -> int:
        """Assess weather severity (1-10 scale)"""
        return random.randint(4, 9)  # Simulated
    
    def assess_historical_precedent(self, context: Dict[str, Any]) -> int:
        """Assess historical precedent (1-10 scale)"""
        return random.randint(3, 8)  # Simulated
    
    def assess_population_density(self, context: Dict[str, Any]) -> int:
        """Assess population density impact (1-10 scale)"""
        return random.randint(5, 9)  # Simulated
    
    def assess_infrastructure_vulnerability(self, context: Dict[str, Any]) -> int:
        """Assess infrastructure vulnerability (1-10 scale)"""
        return random.randint(4, 8)  # Simulated
    
    def assess_response_capacity(self, context: Dict[str, Any]) -> int:
        """Assess emergency response capacity (1-10 scale)"""
        return random.randint(3, 7)  # Simulated
    
    def calculate_geographic_impact(self, factors: Dict[str, int]) -> List[str]:
        """Calculate geographic areas of impact"""
        return ['Urban core', 'Suburban areas', 'Rural communities']
    
    def calculate_correlation_strength(self, factors: Dict[str, int]) -> float:
        """Calculate strength of factor correlation"""
        return 0.75
    
    async def analyze_trends(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze historical trends"""
        return {
            'confidence': 0.8,
            'timespan': '10 years',
            'anomalies': ['Unusual temperature spike in 2023']
        }
    
    def identify_patterns(self, trend_data: Dict[str, Any]) -> List[str]:
        """Identify significant patterns in trends"""
        return [
            'Increasing frequency of extreme heat events',
            'Earlier onset of severe weather seasons',
            'Higher intensity precipitation events'
        ]
    
    def generate_projections(self, patterns: List[str]) -> List[str]:
        """Generate future projections based on patterns"""
        return [
            '15% increase in heat wave days expected over next 5 years',
            'Storm seasons may begin 2 weeks earlier on average'
        ]
    
    def generate_trend_insights(self, patterns: List[str]) -> List[str]:
        """Generate actionable insights from trends"""
        return [
            'Climate adaptation strategies should focus on heat resilience',
            'Emergency preparedness timelines may need adjustment'
        ]
    
    async def assess_vulnerability_factors(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess vulnerability factors for populations"""
        return {
            'score': 7.2,
            'geographic': ['Low-lying coastal areas', 'Urban heat islands'],
            'infrastructure': ['Aging power grid', 'Limited transportation routes'],
            'social': ['Elderly populations', 'Low-income communities']
        }
    
    def calculate_population_impact(self, vulnerability_factors: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate impact on different population groups"""
        return {
            'high_risk_groups': ['Adults 65+', 'Children under 5', 'Outdoor workers'],
            'estimated_affected': 25000
        }
    
    def generate_protection_strategies(self, vulnerability_factors: Dict[str, Any]) -> List[str]:
        """Generate protection strategies for vulnerable populations"""
        return [
            'Establish cooling centers in affected neighborhoods',
            'Implement check-in programs for vulnerable residents',
            'Ensure accessible evacuation transportation'
        ]
    
    def generate_priority_actions(self, population_impact: Dict[str, Any]) -> List[str]:
        """Generate priority actions for population protection"""
        return [
            'Identify and contact high-risk individuals',
            'Prepare accessible emergency shelters',
            'Coordinate with community organizations'
        ]
    
    def generate_risk_timeline(self, risk_factors: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Generate timeline for risk management actions"""
        return {
            'immediate': ['Monitor weather conditions'],
            '6-12 hours': ['Prepare emergency resources'],
            '12-24 hours': ['Issue public advisories'],
            '24+ hours': ['Implement response plans']
        }