const { Agent } = require('@google-cloud/agent-toolkit');
const config = require('../config/environment');

class RootAgent extends Agent {
  constructor() {
    super({
      name: 'root-agent',
      description: 'Primary orchestrator for weather insights and emergency response queries',
      projectId: config.agent.projectId,
      region: config.agent.region
    });
    
    this.capabilities = [
      'user_interaction',
      'query_interpretation',
      'agent_coordination',
      'response_synthesis'
    ];
  }

  async initialize() {
    await super.initialize();
    
    this.tools = [
      {
        name: 'coordinate_agents',
        description: 'Coordinate with specialized agents for complex queries',
        parameters: {
          type: 'object',
          properties: {
            query: { type: 'string' },
            agents_needed: { type: 'array', items: { type: 'string' } },
            priority: { type: 'string', enum: ['low', 'medium', 'high', 'emergency'] }
          }
        }
      },
      {
        name: 'synthesize_response',
        description: 'Combine responses from multiple agents into coherent answer',
        parameters: {
          type: 'object',
          properties: {
            agent_responses: { type: 'array' },
            context: { type: 'object' }
          }
        }
      }
    ];
  }

  async processQuery(userQuery, context = {}) {
    try {
      const queryAnalysis = await this.analyzeQuery(userQuery);
      const requiredAgents = this.determineRequiredAgents(queryAnalysis);
      
      const agentResponses = await Promise.all(
        requiredAgents.map(agent => this.callAgent(agent, userQuery, context))
      );

      return await this.synthesizeResponse(agentResponses, queryAnalysis, context);
    } catch (error) {
      console.error('Root Agent error:', error);
      return {
        error: true,
        message: 'I encountered an issue processing your request. Please try again.',
        timestamp: new Date().toISOString()
      };
    }
  }

  analyzeQuery(query) {
    const keywords = {
      data: ['historical', 'records', 'statistics', 'data', 'trends'],
      forecast: ['forecast', 'prediction', 'upcoming', 'future', 'expected'],
      emergency: ['hurricane', 'tornado', 'flood', 'evacuation', 'emergency', 'disaster'],
      location: ['city', 'county', 'state', 'zip', 'coordinates', 'area']
    };

    const analysis = {
      type: 'general',
      urgency: 'medium',
      location_based: false,
      time_sensitive: false
    };

    if (keywords.emergency.some(word => query.toLowerCase().includes(word))) {
      analysis.urgency = 'high';
      analysis.type = 'emergency';
    }

    if (keywords.forecast.some(word => query.toLowerCase().includes(word))) {
      analysis.type = 'forecast';
      analysis.time_sensitive = true;
    }

    if (keywords.data.some(word => query.toLowerCase().includes(word))) {
      analysis.type = 'data_analysis';
    }

    if (keywords.location.some(word => query.toLowerCase().includes(word))) {
      analysis.location_based = true;
    }

    return analysis;
  }

  determineRequiredAgents(analysis) {
    const agents = [];

    switch (analysis.type) {
      case 'emergency':
        agents.push('forecast-agent', 'data-agent', 'insights-agent');
        break;
      case 'forecast':
        agents.push('forecast-agent');
        if (analysis.location_based) agents.push('data-agent');
        break;
      case 'data_analysis':
        agents.push('data-agent', 'insights-agent');
        break;
      default:
        agents.push('forecast-agent');
    }

    return agents;
  }

  async callAgent(agentName, query, context) {
    const AgentClass = require(`./${agentName.split('-').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)).join('')}`);
    
    const agent = new AgentClass();
    await agent.initialize();
    
    return await agent.processRequest(query, context);
  }

  async synthesizeResponse(responses, analysis, context) {
    const synthesis = {
      summary: '',
      details: [],
      recommendations: [],
      urgency: analysis.urgency,
      timestamp: new Date().toISOString(),
      sources: []
    };

    responses.forEach(response => {
      if (response.summary) synthesis.summary += response.summary + ' ';
      if (response.details) synthesis.details.push(...response.details);
      if (response.recommendations) synthesis.recommendations.push(...response.recommendations);
      if (response.sources) synthesis.sources.push(...response.sources);
    });

    if (analysis.urgency === 'high') {
      synthesis.alert = true;
      synthesis.immediate_actions = this.generateEmergencyActions(responses);
    }

    return synthesis;
  }

  generateEmergencyActions(responses) {
    const actions = [];
    
    responses.forEach(response => {
      if (response.emergency_actions) {
        actions.push(...response.emergency_actions);
      }
    });

    return actions.length > 0 ? actions : [
      'Monitor weather conditions closely',
      'Review emergency preparedness plans',
      'Stay informed through official channels'
    ];
  }
}

module.exports = RootAgent;