from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime
import re
from google.cloud import bigquery
from python_src.agents.base_agent import BaseAgent
from python_src.config.environment import config

logger = logging.getLogger(__name__)

class DataAgent(BaseAgent):
    """Queries BigQuery NOAA datasets for historical weather data and analytics"""
    
    def __init__(self):
        super().__init__(
            name='data-agent',
            description='Queries BigQuery NOAA datasets for historical weather data and analytics'
        )
        self.capabilities = [
            'historical_data_analysis',
            'storm_track_queries',
            'flood_record_analysis',
            'temperature_extremes',
            'precipitation_patterns'
        ]
        self.bigquery_client = None
    
    async def _setup_tools(self):
        """Setup Data Agent specific tools and BigQuery client"""
        self.bigquery_client = bigquery.Client(
            project=config.PROJECT_ID,
            location=config.BIGQUERY_LOCATION
        )
        
        self.tools = [
            {
                'name': 'query_historical_storms',
                'description': 'Query historical storm data from NOAA datasets',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'location': {'type': 'string'},
                        'storm_type': {'type': 'string', 'enum': ['hurricane', 'tornado', 'thunderstorm']},
                        'years_back': {'type': 'number', 'default': 10}
                    }
                }
            },
            {
                'name': 'analyze_flood_risk',
                'description': 'Analyze historical flood data for specific river basins',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'river_basin': {'type': 'string'},
                        'rainfall_rate': {'type': 'number'},
                        'time_period': {'type': 'string'}
                    }
                }
            },
            {
                'name': 'get_temperature_extremes',
                'description': 'Get historical temperature extremes for heat wave analysis',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'location': {'type': 'string'},
                        'duration_hours': {'type': 'number', 'default': 48}
                    }
                }
            }
        ]
    
    async def process_request(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process data analysis request"""
        try:
            query_type = self.classify_data_query(query)
            
            if query_type == 'flood_analysis':
                response_data = await self.handle_flood_analysis(query, context)
            elif query_type == 'storm_history':
                response_data = await self.handle_storm_history(query, context)
            elif query_type == 'temperature_analysis':
                response_data = await self.handle_temperature_analysis(query, context)
            else:
                response_data = await self.handle_general_data_query(query, context)
            
            return self.generate_success_response(response_data, context.get('request_id'))
            
        except Exception as e:
            logger.error(f"Data Agent error: {str(e)}")
            return self.generate_error_response(e, context.get('request_id'))
    
    def classify_data_query(self, query: str) -> str:
        """Classify the type of data query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['flood', 'rainfall', 'river']):
            return 'flood_analysis'
        elif any(word in query_lower for word in ['hurricane', 'storm', 'tornado']):
            return 'storm_history'
        elif any(word in query_lower for word in ['heat', 'temperature', 'cooling']):
            return 'temperature_analysis'
        else:
            return 'general'
    
    async def handle_flood_analysis(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle flood analysis queries"""
        try:
            sql_query = """
                SELECT 
                    year,
                    month,
                    max_precipitation_mm,
                    flood_events,
                    affected_population
                FROM `bigquery-public-data.noaa_historic_severe_storms.storms_*`
                WHERE REGEXP_EXTRACT(_TABLE_SUFFIX, r'[0-9]+') BETWEEN '2010' AND '2023'
                    AND event_type = 'Flood'
                    AND state = @state
                ORDER BY max_precipitation_mm DESC
                LIMIT 50
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter(
                        "state", "STRING", self.extract_location_from_query(query) or "TX"
                    )
                ]
            )
            
            query_job = self.bigquery_client.query(sql_query, job_config=job_config)
            results = query_job.result()
            
            rows = [dict(row) for row in results]
            
            return {
                'summary': f'Found {len(rows)} historical flood events in the specified area',
                'details': [
                    {
                        'date': f"{row['year']}-{row['month']}",
                        'precipitation': row['max_precipitation_mm'],
                        'events': row['flood_events'],
                        'population_affected': row['affected_population']
                    }
                    for row in rows
                ],
                'analysis': self.analyze_flood_data(rows),
                'sources': ['NOAA Historic Severe Storms Dataset'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Flood analysis error: {str(e)}")
            # Return simulated data for demo purposes
            return await self.get_simulated_flood_data(query)
    
    async def handle_storm_history(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle storm history queries"""
        try:
            sql_query = """
                SELECT 
                    name,
                    iso_time,
                    lat,
                    lon,
                    wind_kts,
                    pressure,
                    category,
                    dist2land
                FROM `bigquery-public-data.noaa_hurricanes.hurricanes`
                WHERE season >= EXTRACT(YEAR FROM DATE_SUB(CURRENT_DATE(), INTERVAL 10 YEAR))
                    AND category >= 3
                    AND dist2land <= 100
                ORDER BY wind_kts DESC
                LIMIT 20
            """
            
            query_job = self.bigquery_client.query(sql_query)
            results = query_job.result()
            
            rows = [dict(row) for row in results]
            
            return {
                'summary': f'Found {len(rows)} major hurricanes (Category 3+) within 100 miles of land in the last 10 years',
                'details': [
                    {
                        'name': row['name'],
                        'date': row['iso_time'],
                        'location': [row['lat'], row['lon']],
                        'wind_speed': row['wind_kts'],
                        'pressure': row['pressure'],
                        'category': row['category'],
                        'distance_to_land': row['dist2land']
                    }
                    for row in rows
                ],
                'emergency_actions': self.generate_storm_actions(rows),
                'sources': ['NOAA Hurricane Database'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Storm history error: {str(e)}")
            return await self.get_simulated_storm_data(query)
    
    async def handle_temperature_analysis(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle temperature analysis queries"""
        try:
            sql_query = """
                SELECT 
                    date,
                    temperature_max,
                    temperature_min,
                    heat_index,
                    state
                FROM `bigquery-public-data.noaa_gsod.gsod*`
                WHERE _TABLE_SUFFIX >= FORMAT_DATE('%Y', DATE_SUB(CURRENT_DATE(), INTERVAL 5 YEAR))
                    AND temperature_max > 100
                    AND state = @state
                ORDER BY temperature_max DESC
                LIMIT 30
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter(
                        "state", "STRING", self.extract_location_from_query(query) or "TX"
                    )
                ]
            )
            
            query_job = self.bigquery_client.query(sql_query, job_config=job_config)
            results = query_job.result()
            
            rows = [dict(row) for row in results]
            
            return {
                'summary': f'Found {len(rows)} extreme heat days (>100°F) in the last 5 years',
                'details': [
                    {
                        'date': row['date'],
                        'max_temp': row['temperature_max'],
                        'min_temp': row['temperature_min'],
                        'heat_index': row['heat_index'],
                        'state': row['state']
                    }
                    for row in rows
                ],
                'recommendations': self.generate_heat_recommendations(rows),
                'sources': ['NOAA Global Summary of the Day'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Temperature analysis error: {str(e)}")
            return await self.get_simulated_temperature_data(query)
    
    async def handle_general_data_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general data queries"""
        return {
            'summary': 'General weather data available',
            'details': ['Access to NOAA historical datasets', 'Storm tracking data', 'Temperature records'],
            'capabilities': self.capabilities,
            'sources': ['NOAA BigQuery Public Datasets'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def extract_location_from_query(self, query: str) -> Optional[str]:
        """Extract location (state code) from query"""
        state_regex = r'\b([A-Z]{2})\b'
        match = re.search(state_regex, query)
        return match.group(1) if match else None
    
    def analyze_flood_data(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze flood data for risk assessment"""
        if not data:
            return {'risk_level': 'low', 'probability': 0}
        
        avg_precipitation = sum(row['max_precipitation_mm'] for row in data) / len(data)
        max_precipitation = max(row['max_precipitation_mm'] for row in data)
        
        if avg_precipitation > 50:
            risk_level = 'high'
            probability = 0.7
        elif avg_precipitation > 25:
            risk_level = 'medium'
            probability = 0.4
        else:
            risk_level = 'low'
            probability = 0.2
        
        return {
            'risk_level': risk_level,
            'probability': probability,
            'avg_precipitation': avg_precipitation,
            'max_precipitation': max_precipitation,
            'historical_events': len(data)
        }
    
    def generate_storm_actions(self, storm_data: List[Dict]) -> List[str]:
        """Generate emergency actions based on storm data"""
        actions = []
        
        if any(storm['category'] >= 4 for storm in storm_data):
            actions.extend([
                'Immediate evacuation recommended for coastal areas',
                'Secure or relocate outdoor equipment and vehicles'
            ])
        
        actions.extend([
            'Monitor official weather channels for updates',
            'Ensure emergency supplies are readily available',
            'Review evacuation routes and shelter locations'
        ])
        
        return actions
    
    def generate_heat_recommendations(self, heat_data: List[Dict]) -> List[str]:
        """Generate heat safety recommendations"""
        recommendations = []
        
        if any(day['temperature_max'] > 110 for day in heat_data):
            recommendations.extend([
                'Establish cooling centers for vulnerable populations',
                'Issue heat emergency alerts'
            ])
        
        recommendations.extend([
            'Increase hydration reminders',
            'Limit outdoor activities during peak hours',
            'Check on elderly and vulnerable community members'
        ])
        
        return recommendations
    
    # Simulated data methods for demo purposes
    async def get_simulated_flood_data(self, query: str) -> Dict[str, Any]:
        """Return simulated flood data for demonstration"""
        return {
            'summary': 'Found 15 historical flood events in the specified area (simulated data)',
            'details': [
                {'date': '2023-08', 'precipitation': 89.2, 'events': 3, 'population_affected': 12000},
                {'date': '2022-06', 'precipitation': 67.8, 'events': 2, 'population_affected': 8500},
                {'date': '2021-09', 'precipitation': 78.5, 'events': 4, 'population_affected': 15600}
            ],
            'analysis': {
                'risk_level': 'high',
                'probability': 0.75,
                'avg_precipitation': 78.5,
                'max_precipitation': 89.2,
                'historical_events': 15
            },
            'sources': ['NOAA Historic Severe Storms Dataset (Simulated)'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def get_simulated_storm_data(self, query: str) -> Dict[str, Any]:
        """Return simulated storm data for demonstration"""
        return {
            'summary': 'Found 8 major hurricanes (Category 3+) within 100 miles of land in the last 10 years (simulated data)',
            'details': [
                {'name': 'Hurricane Delta', 'date': '2023-09-15', 'location': [29.2, -94.8], 'wind_speed': 145, 'category': 4},
                {'name': 'Hurricane Gamma', 'date': '2022-08-22', 'location': [28.5, -95.2], 'wind_speed': 125, 'category': 3}
            ],
            'emergency_actions': [
                'Monitor official weather channels for updates',
                'Ensure emergency supplies are readily available',
                'Review evacuation routes and shelter locations'
            ],
            'sources': ['NOAA Hurricane Database (Simulated)'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def get_simulated_temperature_data(self, query: str) -> Dict[str, Any]:
        """Return simulated temperature data for demonstration"""
        return {
            'summary': 'Found 25 extreme heat days (>100°F) in the last 5 years (simulated data)',
            'details': [
                {'date': '2023-07-15', 'max_temp': 112, 'min_temp': 89, 'heat_index': 118, 'state': 'TX'},
                {'date': '2023-07-14', 'max_temp': 108, 'min_temp': 87, 'heat_index': 115, 'state': 'TX'}
            ],
            'recommendations': [
                'Increase hydration reminders',
                'Limit outdoor activities during peak hours',
                'Check on elderly and vulnerable community members'
            ],
            'sources': ['NOAA Global Summary of the Day (Simulated)'],
            'timestamp': datetime.utcnow().isoformat()
        }