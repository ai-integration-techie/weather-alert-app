import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Server Configuration
    PORT = int(os.getenv('PORT', 8080))
    
    # Google Cloud Configuration
    PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
    
    # BigQuery Configuration
    BIGQUERY_DATASET_ID = os.getenv('BIGQUERY_DATASET_ID', 'weather_data')
    BIGQUERY_LOCATION = os.getenv('BIGQUERY_LOCATION', 'US')
    
    # National Weather Service Configuration
    NWS_BASE_URL = 'https://api.weather.gov'
    NWS_USER_AGENT = os.getenv('NWS_USER_AGENT', 'WeatherInsightsAdvisor/1.0')
    
    # Agent Configuration
    AGENT_ENGINE_URL = os.getenv('AGENT_ENGINE_URL')
    AGENT_REGION = os.getenv('AGENT_REGION', 'us-central1')
    
    # Environment
    ENVIRONMENT = os.getenv('NODE_ENV', 'development')
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        required_vars = ['PROJECT_ID']
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

config = Config()