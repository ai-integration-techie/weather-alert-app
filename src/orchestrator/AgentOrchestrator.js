const RootAgent = require('../agents/RootAgent');
const DataAgent = require('../agents/DataAgent');
const ForecastAgent = require('../agents/ForecastAgent');
const InsightsAgent = require('../agents/InsightsAgent');
const config = require('../config/environment');

class AgentOrchestrator {
  constructor() {
    this.agents = new Map();
    this.requestHistory = [];
    this.activeRequests = new Map();
    
    this.agentTypes = {
      'root': RootAgent,
      'data': DataAgent,
      'forecast': ForecastAgent,
      'insights': InsightsAgent
    };
  }

  async initialize() {
    try {
      console.log('Initializing Agent Orchestrator...');
      
      for (const [type, AgentClass] of Object.entries(this.agentTypes)) {
        const agent = new AgentClass();
        await agent.initialize();
        this.agents.set(type, agent);
        console.log(`${type} agent initialized successfully`);
      }
      
      console.log('Agent Orchestrator initialization complete');
      return true;
    } catch (error) {
      console.error('Failed to initialize Agent Orchestrator:', error);
      throw error;
    }
  }

  async processUserQuery(query, context = {}) {
    const requestId = this.generateRequestId();
    const startTime = Date.now();
    
    try {
      console.log(`Processing query [${requestId}]: ${query.substring(0, 100)}...`);
      
      this.activeRequests.set(requestId, {
        query: query,
        context: context,
        startTime: startTime,
        status: 'processing'
      });

      const rootAgent = this.agents.get('root');
      const response = await rootAgent.processQuery(query, {
        ...context,
        requestId: requestId,
        orchestrator: this
      });

      const endTime = Date.now();
      const duration = endTime - startTime;

      this.activeRequests.set(requestId, {
        ...this.activeRequests.get(requestId),
        status: 'completed',
        duration: duration,
        response: response
      });

      this.requestHistory.push({
        requestId: requestId,
        query: query,
        response: response,
        duration: duration,
        timestamp: new Date().toISOString()
      });

      console.log(`Query processed [${requestId}] in ${duration}ms`);
      return this.formatResponse(response, requestId);

    } catch (error) {
      console.error(`Error processing query [${requestId}]:`, error);
      
      this.activeRequests.set(requestId, {
        ...this.activeRequests.get(requestId),
        status: 'error',
        error: error.message
      });

      return this.formatErrorResponse(error, requestId);
    }
  }

  async coordinateAgents(agentTypes, query, context) {
    const coordinationId = this.generateRequestId();
    console.log(`Coordinating agents [${coordinationId}]: ${agentTypes.join(', ')}`);
    
    try {
      const agentPromises = agentTypes.map(async (agentType) => {
        const agent = this.agents.get(agentType);
        if (!agent) {
          throw new Error(`Agent type '${agentType}' not found`);
        }
        
        console.log(`Calling ${agentType} agent...`);
        const response = await agent.processRequest(query, {
          ...context,
          coordinationId: coordinationId
        });
        
        return {
          agentType: agentType,
          response: response,
          timestamp: new Date().toISOString()
        };
      });

      const agentResponses = await Promise.all(agentPromises);
      console.log(`Agent coordination [${coordinationId}] completed`);
      
      return agentResponses;

    } catch (error) {
      console.error(`Agent coordination [${coordinationId}] failed:`, error);
      throw error;
    }
  }

  async handleEmergencyQuery(query, context) {
    console.log('EMERGENCY QUERY DETECTED - Prioritizing response');
    
    const emergencyContext = {
      ...context,
      priority: 'emergency',
      timestamp: new Date().toISOString()
    };

    const requiredAgents = ['forecast', 'data', 'insights'];
    const agentResponses = await this.coordinateAgents(requiredAgents, query, emergencyContext);
    
    const insightsAgent = this.agents.get('insights');
    const emergencyAnalysis = await insightsAgent.processRequest(query, {
      ...emergencyContext,
      agentResponses: agentResponses,
      analysisType: 'emergency_correlation'
    });

    return {
      type: 'emergency_response',
      analysis: emergencyAnalysis,
      agentResponses: agentResponses,
      timestamp: new Date().toISOString(),
      priority: 'critical'
    };
  }

  getAgentStatus() {
    const status = {
      orchestrator: {
        initialized: this.agents.size > 0,
        activeRequests: this.activeRequests.size,
        totalRequests: this.requestHistory.length
      },
      agents: {}
    };

    for (const [type, agent] of this.agents) {
      status.agents[type] = {
        name: agent.name,
        capabilities: agent.capabilities || [],
        initialized: true
      };
    }

    return status;
  }

  getRequestHistory(limit = 10) {
    return this.requestHistory
      .slice(-limit)
      .map(req => ({
        requestId: req.requestId,
        query: req.query.substring(0, 100) + (req.query.length > 100 ? '...' : ''),
        duration: req.duration,
        timestamp: req.timestamp
      }));
  }

  async getAgentCapabilities() {
    const capabilities = {};
    
    for (const [type, agent] of this.agents) {
      capabilities[type] = {
        name: agent.name,
        description: agent.description || `${type} agent for weather insights`,
        capabilities: agent.capabilities || [],
        tools: agent.tools?.map(tool => ({
          name: tool.name,
          description: tool.description
        })) || []
      };
    }
    
    return capabilities;
  }

  formatResponse(response, requestId) {
    return {
      requestId: requestId,
      status: 'success',
      data: response,
      timestamp: new Date().toISOString(),
      agent_system: 'Weather Insights Advisor'
    };
  }

  formatErrorResponse(error, requestId) {
    return {
      requestId: requestId,
      status: 'error',
      error: {
        message: error.message,
        type: error.constructor.name
      },
      timestamp: new Date().toISOString(),
      agent_system: 'Weather Insights Advisor'
    };
  }

  generateRequestId() {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  async shutdown() {
    console.log('Shutting down Agent Orchestrator...');
    
    for (const [type, agent] of this.agents) {
      try {
        if (agent.shutdown) {
          await agent.shutdown();
        }
        console.log(`${type} agent shut down successfully`);
      } catch (error) {
        console.error(`Error shutting down ${type} agent:`, error);
      }
    }
    
    this.agents.clear();
    this.activeRequests.clear();
    console.log('Agent Orchestrator shutdown complete');
  }

  // Health check method
  async healthCheck() {
    const health = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      agents: {},
      system: {
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        activeRequests: this.activeRequests.size
      }
    };

    for (const [type, agent] of this.agents) {
      try {
        health.agents[type] = {
          status: 'healthy',
          initialized: true,
          capabilities: agent.capabilities?.length || 0
        };
      } catch (error) {
        health.agents[type] = {
          status: 'unhealthy',
          error: error.message
        };
        health.status = 'degraded';
      }
    }

    return health;
  }
}

module.exports = AgentOrchestrator;