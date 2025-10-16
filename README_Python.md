# Weather Insights & Forecast Advisor - Python Implementation

A multi-agent system built with Python, FastAPI, and Google Cloud ADK for weather disaster relief and preparedness intelligence.

## Python Architecture

This Python implementation maintains the same multi-agent architecture as the Node.js version:

### Agent Architecture

1. **Root Agent** (`python_src/agents/root_agent.py`) - Primary orchestrator for user interaction and query routing
2. **Data Agent** (`python_src/agents/data_agent.py`) - Queries BigQuery NOAA datasets for historical weather analytics  
3. **Forecast Agent** (`python_src/agents/forecast_agent.py`) - Integrates with National Weather Service API
4. **Insights Agent** (`python_src/agents/insights_agent.py`) - Correlates data and generates actionable intelligence

### Key Python Features

- **FastAPI** - Modern, fast web framework with automatic API documentation
- **Async/Await** - Full asynchronous support for concurrent agent operations
- **Pydantic** - Data validation and serialization
- **Type Hints** - Full type safety throughout the codebase
- **Google Cloud SDK** - Native Python libraries for BigQuery and AI Platform

## Quick Start

### Prerequisites

- Python 3.9+
- Google Cloud Project with BigQuery and Agent Toolkit APIs enabled
- Virtual environment (recommended)

### Installation

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your Google Cloud project details
```

4. **Set up Google Cloud authentication:**
```bash
gcloud auth application-default login
# OR set GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

### Running the Application

#### Development Mode
```bash
python run_python.py
```

#### Production Mode
```bash
python -m uvicorn python_src.main:app --host 0.0.0.0 --port 8080
```

#### Using npm scripts
```bash
npm run start-python
```

## API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8080/docs
- **Alternative Docs**: http://localhost:8080/redoc
- **Health Check**: http://localhost:8080/api/health

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service information |
| POST | `/api/query` | Process weather queries |
| POST | `/api/emergency` | Emergency weather response |
| GET | `/api/status` | Agent system status |
| GET | `/api/capabilities` | Agent capabilities |
| GET | `/api/health` | Health check |
| GET | `/api/history` | Request history |

## Example Usage

### Basic Query
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post("http://localhost:8080/api/query", json={
        "query": "What is the flood risk for Houston, TX based on current rainfall rates?",
        "context": {"location": {"lat": 29.7604, "lon": -95.3698}}
    })
    print(response.json())
```

### Emergency Query
```python
async with httpx.AsyncClient() as client:
    response = await client.post("http://localhost:8080/api/emergency", json={
        "query": "Hurricane Category 3 approaching. Which areas need immediate evacuation?",
        "location": {"lat": 29.7604, "lon": -95.3698},
        "severity": "critical"
    })
    print(response.json())
```

## Deployment

### Google App Engine
```bash
gcloud app deploy app_python.yaml
```

### Docker
```bash
docker build -f Dockerfile.python -t weather-insights-python .
docker run -p 8080:8080 weather-insights-python
```

### Cloud Run
```bash
gcloud run deploy weather-insights-advisor \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Development Features

- **Auto-reload** - Code changes automatically restart the server
- **Type checking** - Full type hints for better IDE support
- **API documentation** - Automatically generated from code
- **Request validation** - Pydantic models validate all inputs
- **Async logging** - Non-blocking request/response logging

## Project Structure

```
python_src/
├── agents/                 # Individual agent implementations
│   ├── base_agent.py      # Abstract base class for agents
│   ├── root_agent.py      # Root orchestrator agent
│   ├── data_agent.py      # BigQuery data analysis agent
│   ├── forecast_agent.py  # NWS API integration agent
│   └── insights_agent.py  # Data correlation and insights
├── config/                # Configuration management
│   └── environment.py     # Environment variables and settings
├── orchestrator/          # Agent coordination
│   └── agent_orchestrator.py  # Multi-agent orchestration
└── main.py               # FastAPI application and server

Additional Files:
├── requirements.txt       # Python dependencies
├── app_python.yaml       # Google App Engine config
├── Dockerfile.python     # Container configuration
└── run_python.py         # Development runner
```

## Comparison with Node.js Version

| Feature | Node.js | Python |
|---------|---------|---------|
| **Web Framework** | Express | FastAPI |
| **Async Support** | Native | asyncio/await |
| **Type Safety** | TypeScript | Type hints |
| **API Docs** | Manual | Auto-generated |
| **Google Cloud** | SDK | Native libraries |
| **Performance** | V8 Engine | CPython |
| **Package Manager** | npm | pip |

## Environment Variables

Same as Node.js version - see main README.md for full list.

## Monitoring and Logging

- **Structured logging** with Python's logging module
- **Request/response tracking** via middleware
- **Health checks** with detailed agent status
- **Metrics collection** ready for integration with monitoring tools

## Contributing

1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Update API documentation in docstrings
4. Test with both development and production configurations

## License

Same as main project - designed for emergency management and public safety applications.