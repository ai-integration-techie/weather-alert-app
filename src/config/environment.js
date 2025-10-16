require('dotenv').config();

module.exports = {
  port: process.env.PORT || 8080,
  projectId: process.env.GOOGLE_CLOUD_PROJECT_ID,
  bigquery: {
    datasetId: process.env.BIGQUERY_DATASET_ID || 'weather_data',
    location: process.env.BIGQUERY_LOCATION || 'US'
  },
  nws: {
    baseUrl: 'https://api.weather.gov',
    userAgent: process.env.NWS_USER_AGENT || 'WeatherInsightsAdvisor/1.0'
  },
  agent: {
    engineUrl: process.env.AGENT_ENGINE_URL,
    projectId: process.env.GOOGLE_CLOUD_PROJECT_ID,
    region: process.env.AGENT_REGION || 'us-central1'
  }
};