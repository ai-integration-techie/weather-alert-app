const { Agent } = require('@google-cloud/agent-toolkit');
const config = require('../config/environment');

class InsightsAgent extends Agent {
  constructor() {
    super({
      name: 'insights-agent',
      description: 'Correlates data and generates natural-language summaries for actionable weather intelligence',
      projectId: config.agent.projectId,
      region: config.agent.region
    });
    
    this.capabilities = [
      'data_correlation',
      'risk_assessment',
      'trend_analysis',
      'emergency_prioritization',
      'natural_language_synthesis'
    ];
  }

  async initialize() {
    await super.initialize();
    
    this.tools = [
      {
        name: 'correlate_historical_forecast',
        description: 'Correlate historical data with current forecasts for risk assessment',
        parameters: {
          type: 'object',
          properties: {
            historical_data: { type: 'object' },
            forecast_data: { type: 'object' },
            location_context: { type: 'object' }
          }
        }
      },
      {
        name: 'assess_population_risk',
        description: 'Assess risk to vulnerable populations based on weather conditions',
        parameters: {
          type: 'object',
          properties: {
            weather_conditions: { type: 'object' },
            demographic_data: { type: 'object' },
            infrastructure_data: { type: 'object' }
          }
        }
      },
      {
        name: 'generate_emergency_summary',
        description: 'Generate actionable emergency response summary',
        parameters: {
          type: 'object',
          properties: {
            severity_level: { type: 'string' },
            affected_areas: { type: 'array' },
            time_sensitive: { type: 'boolean' }
          }
        }
      }
    ];
  }

  async processRequest(query, context) {
    try {
      const analysisType = this.determineAnalysisType(query, context);
      
      switch (analysisType) {
        case 'emergency_correlation':
          return await this.handleEmergencyCorrelation(query, context);
        case 'risk_assessment':
          return await this.handleRiskAssessment(query, context);
        case 'trend_analysis':
          return await this.handleTrendAnalysis(query, context);
        case 'vulnerability_analysis':
          return await this.handleVulnerabilityAnalysis(query, context);
        default:
          return await this.handleGeneralInsights(query, context);
      }
    } catch (error) {
      console.error('Insights Agent error:', error);
      return {
        error: true,
        message: 'Unable to generate insights at this time',
        timestamp: new Date().toISOString()
      };
    }
  }

  determineAnalysisType(query, context) {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('emergency') || lowerQuery.includes('evacuation') || lowerQuery.includes('immediate')) {
      return 'emergency_correlation';
    }
    if (lowerQuery.includes('risk') || lowerQuery.includes('probability') || lowerQuery.includes('chance')) {
      return 'risk_assessment';
    }
    if (lowerQuery.includes('trend') || lowerQuery.includes('pattern') || lowerQuery.includes('historical')) {
      return 'trend_analysis';
    }
    if (lowerQuery.includes('population') || lowerQuery.includes('elderly') || lowerQuery.includes('vulnerable')) {
      return 'vulnerability_analysis';
    }
    
    return 'general_insights';
  }

  async handleEmergencyCorrelation(query, context) {
    const correlationData = await this.correlateEmergencyFactors(context);
    const priorityAssessment = this.assessEmergencyPriority(correlationData);
    
    return {
      summary: this.generateEmergencySummary(correlationData, priorityAssessment),
      details: {
        correlation_factors: correlationData.factors,
        priority_level: priorityAssessment.level,
        time_sensitivity: priorityAssessment.timeframe,
        affected_areas: correlationData.geographic_impact
      },
      recommendations: this.generateEmergencyRecommendations(priorityAssessment),
      emergency_actions: this.generateImmediateActions(priorityAssessment),
      sources: ['Multi-agent correlation analysis'],
      timestamp: new Date().toISOString()
    };
  }

  async handleRiskAssessment(query, context) {
    const riskFactors = await this.identifyRiskFactors(context);
    const riskScore = this.calculateRiskScore(riskFactors);
    const mitigationStrategies = this.generateMitigationStrategies(riskFactors);
    
    return {
      summary: `Risk assessment complete: ${riskScore.level} risk level identified`,
      details: {
        risk_score: riskScore.score,
        risk_level: riskScore.level,
        primary_factors: riskFactors.primary,
        secondary_factors: riskFactors.secondary,
        confidence_level: riskScore.confidence
      },
      recommendations: mitigationStrategies,
      timeline: this.generateRiskTimeline(riskFactors),
      sources: ['Risk assessment correlation'],
      timestamp: new Date().toISOString()
    };
  }

  async handleTrendAnalysis(query, context) {
    const trendData = await this.analyzeTrends(context);
    const patterns = this.identifyPatterns(trendData);
    const projections = this.generateProjections(patterns);
    
    return {
      summary: `Trend analysis reveals ${patterns.length} significant patterns`,
      details: {
        identified_trends: patterns,
        statistical_confidence: trendData.confidence,
        data_span: trendData.timespan,
        anomalies: trendData.anomalies
      },
      projections: projections,
      insights: this.generateTrendInsights(patterns),
      sources: ['Historical trend analysis'],
      timestamp: new Date().toISOString()
    };
  }

  async handleVulnerabilityAnalysis(query, context) {
    const vulnerabilityFactors = await this.assessVulnerabilityFactors(context);
    const populationImpact = this.calculatePopulationImpact(vulnerabilityFactors);
    const protectionStrategies = this.generateProtectionStrategies(vulnerabilityFactors);
    
    return {
      summary: `Vulnerability analysis identifies ${populationImpact.high_risk_groups.length} high-risk population groups`,
      details: {
        vulnerability_score: vulnerabilityFactors.score,
        high_risk_groups: populationImpact.high_risk_groups,
        geographic_factors: vulnerabilityFactors.geographic,
        infrastructure_factors: vulnerabilityFactors.infrastructure,
        social_factors: vulnerabilityFactors.social
      },
      recommendations: protectionStrategies,
      priority_actions: this.generatePriorityActions(populationImpact),
      sources: ['Vulnerability assessment'],
      timestamp: new Date().toISOString()
    };
  }

  async handleGeneralInsights(query, context) {
    return {
      summary: 'General weather insights available',
      details: {
        capabilities: this.capabilities,
        analysis_types: ['emergency_correlation', 'risk_assessment', 'trend_analysis', 'vulnerability_analysis']
      },
      sources: ['Insights Agent'],
      timestamp: new Date().toISOString()
    };
  }

  async correlateEmergencyFactors(context) {
    const factors = {
      weather_severity: this.assessWeatherSeverity(context),
      historical_precedent: this.assessHistoricalPrecedent(context),
      population_density: this.assessPopulationDensity(context),
      infrastructure_vulnerability: this.assessInfrastructureVulnerability(context),
      response_capacity: this.assessResponseCapacity(context)
    };

    const geographic_impact = this.calculateGeographicImpact(factors);
    const correlation_strength = this.calculateCorrelationStrength(factors);

    return {
      factors: factors,
      geographic_impact: geographic_impact,
      correlation_strength: correlation_strength
    };
  }

  assessEmergencyPriority(correlationData) {
    let priorityScore = 0;
    const factors = correlationData.factors;

    if (factors.weather_severity >= 8) priorityScore += 40;
    else if (factors.weather_severity >= 6) priorityScore += 25;
    else if (factors.weather_severity >= 4) priorityScore += 15;

    if (factors.historical_precedent >= 7) priorityScore += 20;
    if (factors.population_density >= 7) priorityScore += 15;
    if (factors.infrastructure_vulnerability >= 6) priorityScore += 15;
    if (factors.response_capacity <= 4) priorityScore += 10;

    let level = 'low';
    let timeframe = '24-48 hours';

    if (priorityScore >= 80) {
      level = 'critical';
      timeframe = 'immediate';
    } else if (priorityScore >= 60) {
      level = 'high';
      timeframe = '2-6 hours';
    } else if (priorityScore >= 40) {
      level = 'medium';
      timeframe = '6-12 hours';
    }

    return {
      level: level,
      score: priorityScore,
      timeframe: timeframe
    };
  }

  generateEmergencySummary(correlationData, priorityAssessment) {
    const level = priorityAssessment.level;
    const timeframe = priorityAssessment.timeframe;
    const factors = Object.keys(correlationData.factors).filter(
      key => correlationData.factors[key] >= 6
    );

    if (level === 'critical') {
      return `CRITICAL: Immediate emergency response required within ${timeframe}. Primary concerns: ${factors.join(', ')}.`;
    } else if (level === 'high') {
      return `HIGH PRIORITY: Emergency preparations needed within ${timeframe}. Key factors: ${factors.join(', ')}.`;
    } else {
      return `Monitoring situation. Preparedness recommended within ${timeframe}. Factors to watch: ${factors.join(', ')}.`;
    }
  }

  generateEmergencyRecommendations(priorityAssessment) {
    const recommendations = [];

    if (priorityAssessment.level === 'critical') {
      recommendations.push('Activate emergency operations center immediately');
      recommendations.push('Issue evacuation orders for high-risk areas');
      recommendations.push('Deploy emergency response teams');
    } else if (priorityAssessment.level === 'high') {
      recommendations.push('Place emergency services on standby');
      recommendations.push('Issue public safety advisories');
      recommendations.push('Prepare evacuation routes and shelters');
    } else {
      recommendations.push('Monitor conditions closely');
      recommendations.push('Review emergency response plans');
      recommendations.push('Inform public of potential risks');
    }

    return recommendations;
  }

  generateImmediateActions(priorityAssessment) {
    const actions = [];

    if (priorityAssessment.timeframe === 'immediate') {
      actions.push('Execute emergency protocols NOW');
      actions.push('Notify all emergency personnel');
      actions.push('Begin public notifications');
    } else if (priorityAssessment.timeframe.includes('hours')) {
      actions.push('Alert emergency management teams');
      actions.push('Prepare public communication systems');
      actions.push('Stage emergency resources');
    }

    return actions;
  }

  async identifyRiskFactors(context) {
    return {
      primary: [
        'Severe weather conditions forecasted',
        'Historical precedent for flooding in area',
        'High population density in affected zone'
      ],
      secondary: [
        'Limited evacuation route capacity',
        'Aging infrastructure',
        'Tourist season population increase'
      ]
    };
  }

  calculateRiskScore(riskFactors) {
    const primaryWeight = 0.7;
    const secondaryWeight = 0.3;
    
    const primaryScore = riskFactors.primary.length * 25;
    const secondaryScore = riskFactors.secondary.length * 15;
    
    const totalScore = (primaryScore * primaryWeight) + (secondaryScore * secondaryWeight);
    
    let level = 'low';
    if (totalScore >= 70) level = 'high';
    else if (totalScore >= 40) level = 'medium';
    
    return {
      score: Math.round(totalScore),
      level: level,
      confidence: 0.85
    };
  }

  generateMitigationStrategies(riskFactors) {
    const strategies = [];
    
    if (riskFactors.primary.some(factor => factor.includes('flood'))) {
      strategies.push('Deploy water rescue teams to high-risk areas');
      strategies.push('Open elevated emergency shelters');
    }
    
    if (riskFactors.secondary.some(factor => factor.includes('infrastructure'))) {
      strategies.push('Inspect critical infrastructure systems');
      strategies.push('Prepare backup power systems');
    }
    
    return strategies;
  }

  // Utility methods for assessment
  assessWeatherSeverity(context) {
    return Math.floor(Math.random() * 10) + 1; // Simplified for demo
  }

  assessHistoricalPrecedent(context) {
    return Math.floor(Math.random() * 10) + 1;
  }

  assessPopulationDensity(context) {
    return Math.floor(Math.random() * 10) + 1;
  }

  assessInfrastructureVulnerability(context) {
    return Math.floor(Math.random() * 10) + 1;
  }

  assessResponseCapacity(context) {
    return Math.floor(Math.random() * 10) + 1;
  }

  calculateGeographicImpact(factors) {
    return ['Urban core', 'Suburban areas', 'Rural communities'];
  }

  calculateCorrelationStrength(factors) {
    return 0.75;
  }

  async analyzeTrends(context) {
    return {
      confidence: 0.8,
      timespan: '10 years',
      anomalies: ['Unusual temperature spike in 2023']
    };
  }

  identifyPatterns(trendData) {
    return [
      'Increasing frequency of extreme heat events',
      'Earlier onset of severe weather seasons',
      'Higher intensity precipitation events'
    ];
  }

  generateProjections(patterns) {
    return [
      '15% increase in heat wave days expected over next 5 years',
      'Storm seasons may begin 2 weeks earlier on average'
    ];
  }

  generateTrendInsights(patterns) {
    return [
      'Climate adaptation strategies should focus on heat resilience',
      'Emergency preparedness timelines may need adjustment'
    ];
  }

  async assessVulnerabilityFactors(context) {
    return {
      score: 7.2,
      geographic: ['Low-lying coastal areas', 'Urban heat islands'],
      infrastructure: ['Aging power grid', 'Limited transportation routes'],
      social: ['Elderly populations', 'Low-income communities']
    };
  }

  calculatePopulationImpact(vulnerabilityFactors) {
    return {
      high_risk_groups: ['Adults 65+', 'Children under 5', 'Outdoor workers'],
      estimated_affected: 25000
    };
  }

  generateProtectionStrategies(vulnerabilityFactors) {
    return [
      'Establish cooling centers in affected neighborhoods',
      'Implement check-in programs for vulnerable residents',
      'Ensure accessible evacuation transportation'
    ];
  }

  generatePriorityActions(populationImpact) {
    return [
      'Identify and contact high-risk individuals',
      'Prepare accessible emergency shelters',
      'Coordinate with community organizations'
    ];
  }

  generateRiskTimeline(riskFactors) {
    return {
      immediate: ['Monitor weather conditions'],
      '6-12 hours': ['Prepare emergency resources'],
      '12-24 hours': ['Issue public advisories'],
      '24+ hours': ['Implement response plans']
    };
  }
}

module.exports = InsightsAgent;