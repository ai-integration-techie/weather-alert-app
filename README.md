# Weather Insights & Forecast Advisor

A multi-agent system built with Google ADK for weather disaster relief and preparedness intelligence.

## Architecture

This system implements a collaborative multi-agent architecture with four specialized agents:

### Agent Roles

1. **Root Agent** - Primary orchestrator for user interaction and query routing
2. **Data Agent** - Queries BigQuery NOAA datasets for historical weather analytics
3. **Forecast Agent** - Integrates with National Weather Service API for current/forecast data
4. **Insights Agent** - Correlates data and generates actionable intelligence

## Key Features

- **Emergency Response Intelligence** - Real-time threat assessment for weather disasters
- **Historical Data Analysis** - Query NOAA datasets for storm patterns, flood risks, temperature extremes
- **Forecast Integration** - Current conditions and multi-day forecasts from NWS
- **Risk Assessment** - AI-powered correlation of historical and forecast data
- **Natural Language Interface** - Ask complex questions about weather threats

## Example Queries

- "We have a Hurricane Category 3 approaching. Which census tracts in the predicted path have a history of major flooding and high elderly populations, requiring immediate evacuation priority?"
- "Show me the 48-hour severe heat risk for this city compared to the duration and intensity of the worst heat wave on record, to help us stage cooling centers."
- "What is the historical probability of a flash flood in this specific river basin when the current NWS rainfall rate is 2 inches/hour to justify deploying water rescue teams?"

## Setup

### Prerequisites

- Node.js 18+
- Google Cloud Project with:
  - BigQuery API enabled
  - Agent Toolkit API enabled
  - Service account with appropriate permissions

### Installation

1. Clone and install dependencies:
```bash
npm install
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Google Cloud project details
```

3. Set up Google Cloud authentication:
```bash
gcloud auth application-default login
# OR set GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

### Development

```bash
npm run dev
```

### Production Deployment

#### Google App Engine
```bash
npm run deploy
```

#### Docker
```bash
docker build -t weather-insights-advisor .
docker run -p 8080:8080 weather-insights-advisor
```

## API Endpoints

- `GET /` - Service information
- `POST /api/query` - Process weather queries
- `POST /api/emergency` - Emergency weather response
- `GET /api/status` - Agent system status
- `GET /api/capabilities` - Agent capabilities
- `GET /api/health` - Health check
- `GET /api/history` - Request history

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_CLOUD_PROJECT_ID` | Your Google Cloud project ID | Yes |
| `BIGQUERY_DATASET_ID` | BigQuery dataset for weather data | No (default: weather_data) |
| `AGENT_REGION` | Google Cloud region for agents | No (default: us-central1) |
| `NWS_USER_AGENT` | User agent for NWS API requests | Yes |
| `PORT` | Server port | No (default: 8080) |

## Data Sources

- **NOAA BigQuery Public Datasets**
  - Historical severe storms
  - Hurricane tracking data
  - Global summary weather data
- **National Weather Service API**
  - Current conditions
  - Forecasts and alerts
  - Severe weather warnings

## Agent Communication

The system uses Google ADK's Agent-to-Agent (A2A) communication pattern for coordinated responses:

1. Root Agent receives and analyzes user queries
2. Determines which specialized agents are needed
3. Coordinates parallel data gathering from relevant agents
4. Insights Agent correlates responses for actionable intelligence

## Security

- Helmet.js for security headers
- CORS protection
- Rate limiting (production)
- Environment variable protection
- Service account authentication

## Monitoring

Built-in endpoints for system monitoring:
- Health checks at `/api/health`
- Agent status at `/api/status`
- Request history at `/api/history`

## License

This project is designed for emergency management and public safety applications.