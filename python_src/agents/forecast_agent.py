from typing import Dict, List, Any, Optional, Tuple
import asyncio
import logging
import re
from datetime import datetime
import httpx
from python_src.agents.base_agent import BaseAgent
from python_src.config.environment import config

logger = logging.getLogger(__name__)

class ForecastAgent(BaseAgent):
    """Retrieves current and forecast weather data from National Weather Service API"""
    
    def __init__(self):
        super().__init__(
            name='forecast-agent',
            description='Retrieves current and forecast weather data from National Weather Service API'
        )
        self.capabilities = [
            'current_conditions',
            'forecast_retrieval',
            'severe_weather_alerts',
            'hurricane_tracking',
            'temperature_forecasts'
        ]
        self.http_client = None
    
    async def _setup_tools(self):
        """Setup Forecast Agent specific tools and HTTP client"""
        self.http_client = httpx.AsyncClient(
            base_url=config.NWS_BASE_URL,
            headers={'User-Agent': config.NWS_USER_AGENT},
            timeout=10.0
        )
        
        self.tools = [
            {
                'name': 'get_current_conditions',
                'description': 'Get current weather conditions for a location',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'latitude': {'type': 'number'},
                        'longitude': {'type': 'number'}
                    },
                    'required': ['latitude', 'longitude']
                }
            },
            {
                'name': 'get_forecast',
                'description': 'Get weather forecast for a location',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'latitude': {'type': 'number'},
                        'longitude': {'type': 'number'},
                        'days': {'type': 'number', 'default': 7}
                    },
                    'required': ['latitude', 'longitude']
                }
            },
            {
                'name': 'get_severe_alerts',
                'description': 'Get active severe weather alerts for a location',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'state': {'type': 'string'},
                        'zone': {'type': 'string'}
                    }
                }
            }
        ]
    
    async def process_request(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process forecast request"""
        try:
            request_type = self.classify_forecast_request(query)
            location = await self.extract_location_from_query(query, context)
            
            if request_type == 'current_conditions':
                response_data = await self.handle_current_conditions(location, context)
            elif request_type == 'forecast':
                response_data = await self.handle_forecast(location, context)
            elif request_type == 'severe_alerts':
                response_data = await self.handle_severe_alerts(location, context)
            elif request_type == 'hurricane_tracking':
                response_data = await self.handle_hurricane_tracking(location, context)
            else:
                response_data = await self.handle_general_forecast(location, context)
            
            return self.generate_success_response(response_data, context.get('request_id'))
            
        except Exception as e:
            logger.error(f"Forecast Agent error: {str(e)}")
            return self.generate_error_response(e, context.get('request_id'))
    
    def classify_forecast_request(self, query: str) -> str:
        """Classify the type of forecast request"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['current', 'now', 'today']):
            return 'current_conditions'
        elif any(word in query_lower for word in ['alert', 'warning', 'watch']):
            return 'severe_alerts'
        elif any(word in query_lower for word in ['hurricane', 'tropical']):
            return 'hurricane_tracking'
        elif any(word in query_lower for word in ['forecast', 'tomorrow', 'week']):
            return 'forecast'
        else:
            return 'general_forecast'
    
    async def extract_location_from_query(self, query: str, context: Dict[str, Any]) -> Dict[str, float]:
        """Extract location coordinates from query or context"""
        # Default location (Dallas, TX)
        default_location = {'lat': 32.7767, 'lon': -96.7970}
        
        if 'location' in context:
            return context['location']
        
        # Try to extract ZIP code
        zip_match = re.search(r'\b\d{5}\b', query)
        if zip_match:
            return await self.geocode_zip_code(zip_match.group())
        
        # Try to extract city, state
        city_state_match = re.search(r'([A-Za-z\s]+),\s*([A-Z]{2})', query)
        if city_state_match:
            city = city_state_match.group(1).strip()
            state = city_state_match.group(2)
            return await self.geocode_city_state(city, state)
        
        return default_location
    
    async def geocode_zip_code(self, zip_code: str) -> Dict[str, float]:
        """Geocode ZIP code to coordinates (simplified)"""
        # In a real implementation, you'd use a geocoding service
        # For demo, return default location
        return {'lat': 32.7767, 'lon': -96.7970}
    
    async def geocode_city_state(self, city: str, state: str) -> Dict[str, float]:
        """Geocode city/state to coordinates (simplified)"""
        # In a real implementation, you'd use a geocoding service
        # For demo, return default location
        return {'lat': 32.7767, 'lon': -96.7970}
    
    async def handle_current_conditions(self, location: Dict[str, float], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle current conditions request"""
        try:
            # Get point information
            point_response = await self.http_client.get(f"/points/{location['lat']},{location['lon']}")
            point_data = point_response.json()
            
            # Get observation stations
            stations_url = point_data['properties']['observationStations']
            stations_response = await self.http_client.get(stations_url)
            stations_data = stations_response.json()
            
            # Get latest observation
            station_id = stations_data['features'][0]['properties']['stationIdentifier']
            obs_response = await self.http_client.get(f"/stations/{station_id}/observations/latest")
            observation = obs_response.json()['properties']
            
            return {
                'summary': f"Current conditions: {observation.get('textDescription', 'Clear')}",
                'details': {
                    'temperature': self.convert_celsius_to_fahrenheit(observation.get('temperature', {}).get('value')),
                    'humidity': observation.get('relativeHumidity', {}).get('value'),
                    'wind_speed': self.convert_mps_to_mph(observation.get('windSpeed', {}).get('value')),
                    'wind_direction': observation.get('windDirection', {}).get('value'),
                    'pressure': observation.get('barometricPressure', {}).get('value'),
                    'visibility': self.convert_meters_to_miles(observation.get('visibility', {}).get('value')),
                    'description': observation.get('textDescription')
                },
                'location': location,
                'timestamp': observation.get('timestamp'),
                'sources': ['National Weather Service']
            }
            
        except Exception as e:
            logger.error(f"Current conditions error: {str(e)}")
            return await self.get_simulated_current_conditions(location)
    
    async def handle_forecast(self, location: Dict[str, float], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle forecast request"""
        try:
            # Get point information
            point_response = await self.http_client.get(f"/points/{location['lat']},{location['lon']}")
            point_data = point_response.json()
            
            # Get forecast
            forecast_url = point_data['properties']['forecast']
            forecast_response = await self.http_client.get(forecast_url)
            forecast_data = forecast_response.json()
            
            periods = forecast_data['properties']['periods']
            severity_assessment = self.assess_forecast_severity(periods)
            
            return {
                'summary': f"{len(periods)}-day forecast available",
                'details': [
                    {
                        'name': period['name'],
                        'temperature': period['temperature'],
                        'temperature_unit': period['temperatureUnit'],
                        'wind_speed': period['windSpeed'],
                        'wind_direction': period['windDirection'],
                        'description': period['detailedForecast'],
                        'is_daytime': period['isDaytime']
                    }
                    for period in periods[:14]
                ],
                'severity': severity_assessment,
                'emergency_actions': self.generate_forecast_actions(periods) if severity_assessment['level'] == 'high' else [],
                'location': location,
                'sources': ['National Weather Service'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Forecast error: {str(e)}")
            return await self.get_simulated_forecast(location)
    
    async def handle_severe_alerts(self, location: Dict[str, float], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle severe weather alerts request"""
        try:
            # Get point information to find zone
            point_response = await self.http_client.get(f"/points/{location['lat']},{location['lon']}")
            point_data = point_response.json()
            
            zone = point_data['properties']['forecastZone'].split('/')[-1]
            
            # Get active alerts
            alerts_response = await self.http_client.get(f"/alerts?zone={zone}&status=actual")
            alerts_data = alerts_response.json()
            
            alerts = alerts_data['features']
            active_alerts = [
                alert for alert in alerts
                if datetime.fromisoformat(alert['properties']['expires'].replace('Z', '+00:00')) > datetime.now()
            ]
            
            return {
                'summary': f"{len(active_alerts)} active weather alerts",
                'details': [
                    {
                        'event': alert['properties']['event'],
                        'severity': alert['properties']['severity'],
                        'urgency': alert['properties']['urgency'],
                        'description': alert['properties']['description'],
                        'instructions': alert['properties'].get('instruction'),
                        'onset': alert['properties']['onset'],
                        'expires': alert['properties']['expires'],
                        'areas': alert['properties']['areaDesc']
                    }
                    for alert in active_alerts
                ],
                'emergency_actions': self.generate_alert_actions(active_alerts),
                'location': location,
                'sources': ['National Weather Service'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Severe alerts error: {str(e)}")
            return await self.get_simulated_alerts(location)
    
    async def handle_hurricane_tracking(self, location: Dict[str, float], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle hurricane tracking request"""
        try:
            # Get active storms (simplified - would need specialized endpoints)
            return {
                'summary': 'Hurricane tracking data available',
                'details': {
                    'message': 'Hurricane tracking requires additional specialized endpoints',
                    'recommendation': 'Monitor Hurricane Database and storm-specific advisories'
                },
                'emergency_actions': [
                    'Monitor National Hurricane Center advisories',
                    'Review evacuation plans if in coastal areas',
                    'Prepare emergency supplies'
                ],
                'sources': ['National Weather Service', 'National Hurricane Center'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Hurricane tracking error: {str(e)}")
            return await self.get_simulated_hurricane_data(location)
    
    async def handle_general_forecast(self, location: Dict[str, float], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general forecast request"""
        return await self.handle_forecast(location, context)
    
    def assess_forecast_severity(self, periods: List[Dict]) -> Dict[str, Any]:
        """Assess severity of forecast conditions"""
        severity_score = 0
        severity_factors = []
        
        for period in periods[:7]:  # Check first week
            description = period['detailedForecast'].lower()
            
            if any(word in description for word in ['severe', 'dangerous']):
                severity_score += 3
                severity_factors.append('Severe weather conditions forecasted')
            
            if any(word in description for word in ['storm', 'thunderstorm']):
                severity_score += 2
                severity_factors.append('Storm activity expected')
            
            if period['temperature'] > 100 or period['temperature'] < 20:
                severity_score += 2
                severity_factors.append('Extreme temperature conditions')
            
            if any(word in description for word in ['flood', 'heavy rain']):
                severity_score += 2
                severity_factors.append('Flooding potential')
        
        level = 'low'
        if severity_score >= 6:
            level = 'high'
        elif severity_score >= 3:
            level = 'medium'
        
        return {
            'level': level,
            'score': severity_score,
            'factors': severity_factors
        }
    
    def generate_forecast_actions(self, periods: List[Dict]) -> List[str]:
        """Generate emergency actions based on forecast"""
        actions = []
        
        for period in periods[:3]:  # Check next 3 periods
            description = period['detailedForecast'].lower()
            
            if 'storm' in description:
                actions.append('Secure outdoor objects and equipment')
            if 'flood' in description:
                actions.append('Avoid low-lying areas and underpasses')
            if period['temperature'] > 100:
                actions.append('Implement heat safety protocols')
            if period['temperature'] < 32:
                actions.append('Protect pipes and outdoor plants from freezing')
        
        return list(set(actions))  # Remove duplicates
    
    def generate_alert_actions(self, alerts: List[Dict]) -> List[str]:
        """Generate emergency actions based on alerts"""
        actions = []
        
        for alert in alerts:
            severity = alert['properties']['severity']
            event = alert['properties']['event'].lower()
            
            if severity in ['Extreme', 'Severe']:
                actions.append('Take immediate protective action')
            
            if 'tornado' in event:
                actions.append('Seek sturdy shelter immediately')
            elif 'hurricane' in event:
                actions.append('Follow evacuation orders if issued')
            elif 'flood' in event:
                actions.append('Move to higher ground')
            
            if alert['properties'].get('instruction'):
                instruction = alert['properties']['instruction']
                actions.append(f"Official guidance: {instruction[:100]}...")
        
        return list(set(actions))
    
    # Utility conversion methods
    def convert_celsius_to_fahrenheit(self, celsius: Optional[float]) -> Optional[int]:
        """Convert Celsius to Fahrenheit"""
        return round((celsius * 9/5) + 32) if celsius is not None else None
    
    def convert_mps_to_mph(self, mps: Optional[float]) -> Optional[int]:
        """Convert meters per second to miles per hour"""
        return round(mps * 2.237) if mps is not None else None
    
    def convert_meters_to_miles(self, meters: Optional[float]) -> Optional[int]:
        """Convert meters to miles"""
        return round(meters * 0.000621371) if meters is not None else None
    
    # Simulated data methods for demo purposes
    async def get_simulated_current_conditions(self, location: Dict[str, float]) -> Dict[str, Any]:
        """Return simulated current conditions for demonstration"""
        return {
            'summary': 'Current conditions: Partly cloudy (simulated data)',
            'details': {
                'temperature': 78,
                'humidity': 65,
                'wind_speed': 12,
                'wind_direction': 225,
                'pressure': 30.15,
                'visibility': 10,
                'description': 'Partly cloudy skies'
            },
            'location': location,
            'timestamp': datetime.utcnow().isoformat(),
            'sources': ['National Weather Service (Simulated)']
        }
    
    async def get_simulated_forecast(self, location: Dict[str, float]) -> Dict[str, Any]:
        """Return simulated forecast for demonstration"""
        return {
            'summary': '7-day forecast available (simulated data)',
            'details': [
                {
                    'name': 'Today',
                    'temperature': 85,
                    'temperature_unit': 'F',
                    'wind_speed': '10 mph',
                    'wind_direction': 'SW',
                    'description': 'Sunny with occasional clouds',
                    'is_daytime': True
                },
                {
                    'name': 'Tonight',
                    'temperature': 68,
                    'temperature_unit': 'F',
                    'wind_speed': '5 mph',
                    'wind_direction': 'S',
                    'description': 'Clear skies',
                    'is_daytime': False
                }
            ],
            'severity': {'level': 'low', 'score': 1, 'factors': []},
            'emergency_actions': [],
            'location': location,
            'sources': ['National Weather Service (Simulated)'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def get_simulated_alerts(self, location: Dict[str, float]) -> Dict[str, Any]:
        """Return simulated alerts for demonstration"""
        return {
            'summary': '1 active weather alert (simulated data)',
            'details': [
                {
                    'event': 'Heat Advisory',
                    'severity': 'Minor',
                    'urgency': 'Expected',
                    'description': 'Hot temperatures expected this afternoon',
                    'instructions': 'Stay hydrated and avoid prolonged outdoor exposure',
                    'onset': datetime.utcnow().isoformat(),
                    'expires': datetime.utcnow().isoformat(),
                    'areas': 'Dallas County'
                }
            ],
            'emergency_actions': ['Stay hydrated', 'Limit outdoor activities'],
            'location': location,
            'sources': ['National Weather Service (Simulated)'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def get_simulated_hurricane_data(self, location: Dict[str, float]) -> Dict[str, Any]:
        """Return simulated hurricane data for demonstration"""
        return {
            'summary': 'No active hurricanes currently tracked (simulated data)',
            'details': {
                'message': 'Hurricane season monitoring active',
                'recommendation': 'Continue monitoring National Hurricane Center'
            },
            'emergency_actions': [
                'Review hurricane preparedness plans',
                'Monitor weather updates regularly'
            ],
            'sources': ['National Hurricane Center (Simulated)'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def shutdown(self):
        """Cleanup HTTP client"""
        if self.http_client:
            await self.http_client.aclose()
        await super().shutdown()