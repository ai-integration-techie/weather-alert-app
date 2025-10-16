const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const AgentOrchestrator = require('./orchestrator/AgentOrchestrator');
const config = require('./config/environment');

class WeatherInsightsAdvisor {
  constructor() {
    this.app = express();
    this.orchestrator = new AgentOrchestrator();
    this.setupMiddleware();
    this.setupRoutes();
  }

  setupMiddleware() {
    this.app.use(helmet());
    this.app.use(cors());
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true }));
    
    this.app.use((req, res, next) => {
      console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
      next();
    });
  }

  setupRoutes() {
    this.app.get('/', (req, res) => {
      res.json({
        name: 'Weather Insights & Forecast Advisor',
        description: 'Multi-agent system for weather disaster relief and preparedness',
        version: '1.0.0',
        agents: ['Root Agent', 'Data Agent', 'Forecast Agent', 'Insights Agent'],
        capabilities: [
          'Weather disaster relief intelligence',
          'Emergency preparedness analysis',
          'Historical weather data correlation',
          'Real-time forecast integration',
          'Risk assessment and insights'
        ]
      });
    });

    this.app.post('/api/query', async (req, res) => {
      try {
        const { query, context = {} } = req.body;
        
        if (!query) {
          return res.status(400).json({
            error: 'Query is required',
            status: 'error'
          });
        }

        const response = await this.orchestrator.processUserQuery(query, {
          ...context,
          userAgent: req.get('User-Agent'),
          ip: req.ip,
          timestamp: new Date().toISOString()
        });

        res.json(response);
      } catch (error) {
        console.error('Query processing error:', error);
        res.status(500).json({
          error: 'Internal server error',
          status: 'error',
          timestamp: new Date().toISOString()
        });
      }
    });

    this.app.post('/api/emergency', async (req, res) => {
      try {
        const { query, location, severity } = req.body;
        
        if (!query) {
          return res.status(400).json({
            error: 'Emergency query is required',
            status: 'error'
          });
        }

        const emergencyContext = {
          priority: 'emergency',
          location: location,
          severity: severity || 'high',
          timestamp: new Date().toISOString()
        };

        const response = await this.orchestrator.handleEmergencyQuery(query, emergencyContext);
        
        res.json({
          status: 'success',
          type: 'emergency_response',
          data: response,
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        console.error('Emergency query processing error:', error);
        res.status(500).json({
          error: 'Failed to process emergency query',
          status: 'error',
          timestamp: new Date().toISOString()
        });
      }
    });

    this.app.get('/api/status', async (req, res) => {
      try {
        const status = this.orchestrator.getAgentStatus();
        res.json({
          status: 'operational',
          ...status,
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        console.error('Status check error:', error);
        res.status(500).json({
          status: 'error',
          error: error.message,
          timestamp: new Date().toISOString()
        });
      }
    });

    this.app.get('/api/capabilities', async (req, res) => {
      try {
        const capabilities = await this.orchestrator.getAgentCapabilities();
        res.json({
          status: 'success',
          capabilities: capabilities,
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        console.error('Capabilities check error:', error);
        res.status(500).json({
          status: 'error',
          error: error.message,
          timestamp: new Date().toISOString()
        });
      }
    });

    this.app.get('/api/health', async (req, res) => {
      try {
        const health = await this.orchestrator.healthCheck();
        const statusCode = health.status === 'healthy' ? 200 : 503;
        res.status(statusCode).json(health);
      } catch (error) {
        console.error('Health check error:', error);
        res.status(503).json({
          status: 'unhealthy',
          error: error.message,
          timestamp: new Date().toISOString()
        });
      }
    });

    this.app.get('/api/history', (req, res) => {
      try {
        const limit = parseInt(req.query.limit) || 10;
        const history = this.orchestrator.getRequestHistory(limit);
        res.json({
          status: 'success',
          history: history,
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        console.error('History retrieval error:', error);
        res.status(500).json({
          status: 'error',
          error: error.message,
          timestamp: new Date().toISOString()
        });
      }
    });

    this.app.use((req, res) => {
      res.status(404).json({
        error: 'Endpoint not found',
        status: 'error',
        available_endpoints: [
          'GET /',
          'POST /api/query',
          'POST /api/emergency',
          'GET /api/status',
          'GET /api/capabilities',
          'GET /api/health',
          'GET /api/history'
        ]
      });
    });

    this.app.use((error, req, res, next) => {
      console.error('Unhandled error:', error);
      res.status(500).json({
        error: 'Internal server error',
        status: 'error',
        timestamp: new Date().toISOString()
      });
    });
  }

  async start() {
    try {
      console.log('Starting Weather Insights Advisor...');
      
      await this.orchestrator.initialize();
      console.log('Agent orchestrator initialized successfully');

      const server = this.app.listen(config.port, () => {
        console.log(`Weather Insights Advisor running on port ${config.port}`);
        console.log(`Access the service at: http://localhost:${config.port}`);
        console.log('Available endpoints:');
        console.log('  GET  /                 - Service information');
        console.log('  POST /api/query        - Process weather queries');
        console.log('  POST /api/emergency    - Emergency weather response');
        console.log('  GET  /api/status       - Agent system status');
        console.log('  GET  /api/capabilities - Agent capabilities');
        console.log('  GET  /api/health       - Health check');
        console.log('  GET  /api/history      - Request history');
      });

      process.on('SIGTERM', () => this.shutdown(server));
      process.on('SIGINT', () => this.shutdown(server));

      return server;
    } catch (error) {
      console.error('Failed to start Weather Insights Advisor:', error);
      process.exit(1);
    }
  }

  async shutdown(server) {
    console.log('Shutting down Weather Insights Advisor...');
    
    try {
      if (server) {
        server.close(() => {
          console.log('HTTP server closed');
        });
      }
      
      await this.orchestrator.shutdown();
      console.log('Weather Insights Advisor shutdown complete');
      process.exit(0);
    } catch (error) {
      console.error('Error during shutdown:', error);
      process.exit(1);
    }
  }
}

if (require.main === module) {
  const app = new WeatherInsightsAdvisor();
  app.start();
}

module.exports = WeatherInsightsAdvisor;