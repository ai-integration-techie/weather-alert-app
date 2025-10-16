const { Agent } = require('@google-cloud/agent-toolkit');
const axios = require('axios');
const config = require('../config/environment');

class ForecastAgent extends Agent {
  constructor() {
    super({
      name: 'forecast-agent',
      description: 'Retrieves current and forecast weather data from National Weather Service API',
      projectId: config.agent.projectId,
      region: config.agent.region
    });
    
    this.nwsClient = axios.create({
      baseURL: config.nws.baseUrl,
      headers: {
        'User-Agent': config.nws.userAgent
      },
      timeout: 10000
    });
    
    this.capabilities = [
      'current_conditions',
      'forecast_retrieval',
      'severe_weather_alerts',
      'hurricane_tracking',
      'temperature_forecasts'
    ];
  }

  async initialize() {
    await super.initialize();
    
    this.tools = [
      {
        name: 'get_current_conditions',
        description: 'Get current weather conditions for a location',
        parameters: {
          type: 'object',
          properties: {
            latitude: { type: 'number' },
            longitude: { type: 'number' }
          },
          required: ['latitude', 'longitude']
        }
      },
      {
        name: 'get_forecast',
        description: 'Get weather forecast for a location',
        parameters: {
          type: 'object',
          properties: {
            latitude: { type: 'number' },
            longitude: { type: 'number' },
            days: { type: 'number', default: 7 }
          },
          required: ['latitude', 'longitude']
        }
      },
      {
        name: 'get_severe_alerts',
        description: 'Get active severe weather alerts for a location',
        parameters: {
          type: 'object',
          properties: {
            state: { type: 'string' },
            zone: { type: 'string' }
          }
        }
      }
    ];
  }

  async processRequest(query, context) {
    try {
      const requestType = this.classifyRequest(query);
      const location = await this.extractLocationFromQuery(query, context);
      
      switch (requestType) {
        case 'current_conditions':
          return await this.handleCurrentConditions(location, context);
        case 'forecast':
          return await this.handleForecast(location, context);
        case 'severe_alerts':
          return await this.handleSevereAlerts(location, context);
        case 'hurricane_tracking':
          return await this.handleHurricaneTracking(location, context);
        default:
          return await this.handleGeneralForecast(location, context);
      }
    } catch (error) {
      console.error('Forecast Agent error:', error);
      return {
        error: true,
        message: 'Unable to retrieve weather forecast at this time',
        timestamp: new Date().toISOString()
      };
    }
  }

  classifyRequest(query) {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('current') || lowerQuery.includes('now') || lowerQuery.includes('today')) {
      return 'current_conditions';
    }
    if (lowerQuery.includes('alert') || lowerQuery.includes('warning') || lowerQuery.includes('watch')) {
      return 'severe_alerts';
    }
    if (lowerQuery.includes('hurricane') || lowerQuery.includes('tropical')) {
      return 'hurricane_tracking';
    }
    if (lowerQuery.includes('forecast') || lowerQuery.includes('tomorrow') || lowerQuery.includes('week')) {
      return 'forecast';
    }
    
    return 'general_forecast';
  }

  async extractLocationFromQuery(query, context) {
    const defaultLocation = { lat: 32.7767, lon: -96.7970 }; // Dallas, TX
    
    if (context.location) {
      return context.location;
    }
    
    const zipCodeMatch = query.match(/\b\d{5}\b/);
    if (zipCodeMatch) {
      return await this.geocodeZipCode(zipCodeMatch[0]);
    }
    
    const cityStateMatch = query.match(/([A-Za-z\s]+),\s*([A-Z]{2})/);
    if (cityStateMatch) {
      return await this.geocodeCityState(cityStateMatch[1].trim(), cityStateMatch[2]);
    }
    
    return defaultLocation;
  }

  async geocodeZipCode(zipCode) {
    try {
      const response = await this.nwsClient.get(`/points/${zipCode}`);
      return {
        lat: response.data.geometry.coordinates[1],
        lon: response.data.geometry.coordinates[0]
      };
    } catch (error) {
      return { lat: 32.7767, lon: -96.7970 }; // Default fallback
    }
  }

  async geocodeCityState(city, state) {
    return { lat: 32.7767, lon: -96.7970 }; // Simplified - in production, use proper geocoding
  }

  async handleCurrentConditions(location, context) {
    try {
      const pointResponse = await this.nwsClient.get(`/points/${location.lat},${location.lon}`);
      const stationUrl = pointResponse.data.properties.observationStations;
      
      const stationsResponse = await this.nwsClient.get(stationUrl);
      const stationId = stationsResponse.data.features[0].properties.stationIdentifier;
      
      const observationResponse = await this.nwsClient.get(`/stations/${stationId}/observations/latest`);
      const observation = observationResponse.data.properties;
      
      return {
        summary: `Current conditions: ${observation.textDescription || 'Clear'}`,
        details: {
          temperature: this.convertCelsiusToFahrenheit(observation.temperature?.value),
          humidity: observation.relativeHumidity?.value,
          wind_speed: this.convertMpsToMph(observation.windSpeed?.value),
          wind_direction: observation.windDirection?.value,
          pressure: observation.barometricPressure?.value,
          visibility: this.convertMetersToMiles(observation.visibility?.value),
          description: observation.textDescription
        },
        location: location,
        timestamp: observation.timestamp,
        sources: ['National Weather Service']
      };
    } catch (error) {
      throw new Error(`Failed to get current conditions: ${error.message}`);
    }
  }

  async handleForecast(location, context) {
    try {
      const pointResponse = await this.nwsClient.get(`/points/${location.lat},${location.lon}`);
      const forecastUrl = pointResponse.data.properties.forecast;
      
      const forecastResponse = await this.nwsClient.get(forecastUrl);
      const periods = forecastResponse.data.properties.periods;
      
      const severityAssessment = this.assessForecastSeverity(periods);
      
      return {
        summary: `${periods.length}-day forecast available`,
        details: periods.slice(0, 14).map(period => ({
          name: period.name,
          temperature: period.temperature,
          temperature_unit: period.temperatureUnit,
          wind_speed: period.windSpeed,
          wind_direction: period.windDirection,
          description: period.detailedForecast,
          is_daytime: period.isDaytime
        })),
        severity: severityAssessment,
        emergency_actions: severityAssessment.level === 'high' ? this.generateForecastActions(periods) : [],
        location: location,
        sources: ['National Weather Service'],
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Failed to get forecast: ${error.message}`);
    }
  }

  async handleSevereAlerts(location, context) {
    try {
      const pointResponse = await this.nwsClient.get(`/points/${location.lat},${location.lon}`);
      const zone = pointResponse.data.properties.forecastZone.split('/').pop();
      
      const alertsResponse = await this.nwsClient.get(`/alerts?zone=${zone}&status=actual`);
      const alerts = alertsResponse.data.features;
      
      const activeAlerts = alerts.filter(alert => 
        new Date(alert.properties.expires) > new Date()
      );
      
      return {
        summary: `${activeAlerts.length} active weather alerts`,
        details: activeAlerts.map(alert => ({
          event: alert.properties.event,
          severity: alert.properties.severity,
          urgency: alert.properties.urgency,
          description: alert.properties.description,
          instructions: alert.properties.instruction,
          onset: alert.properties.onset,
          expires: alert.properties.expires,
          areas: alert.properties.areaDesc
        })),
        emergency_actions: this.generateAlertActions(activeAlerts),
        location: location,
        sources: ['National Weather Service'],
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Failed to get severe alerts: ${error.message}`);
    }
  }

  async handleHurricaneTracking(location, context) {
    try {
      const activeStormsResponse = await this.nwsClient.get('/products/types/TCPAT1');
      
      return {
        summary: 'Hurricane tracking data available',
        details: {
          message: 'Hurricane tracking requires additional specialized endpoints',
          recommendation: 'Monitor Hurricane Database and storm-specific advisories'
        },
        emergency_actions: [
          'Monitor National Hurricane Center advisories',
          'Review evacuation plans if in coastal areas',
          'Prepare emergency supplies'
        ],
        sources: ['National Weather Service', 'National Hurricane Center'],
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        summary: 'Hurricane tracking temporarily unavailable',
        details: { error: error.message },
        sources: ['National Weather Service'],
        timestamp: new Date().toISOString()
      };
    }
  }

  async handleGeneralForecast(location, context) {
    return await this.handleForecast(location, context);
  }

  assessForecastSeverity(periods) {
    let severityScore = 0;
    const severityFactors = [];
    
    periods.slice(0, 7).forEach(period => {
      const description = period.detailedForecast.toLowerCase();
      
      if (description.includes('severe') || description.includes('dangerous')) {
        severityScore += 3;
        severityFactors.push('Severe weather conditions forecasted');
      }
      
      if (description.includes('storm') || description.includes('thunderstorm')) {
        severityScore += 2;
        severityFactors.push('Storm activity expected');
      }
      
      if (period.temperature > 100 || period.temperature < 20) {
        severityScore += 2;
        severityFactors.push('Extreme temperature conditions');
      }
      
      if (description.includes('flood') || description.includes('heavy rain')) {
        severityScore += 2;
        severityFactors.push('Flooding potential');
      }
    });
    
    let level = 'low';
    if (severityScore >= 6) level = 'high';
    else if (severityScore >= 3) level = 'medium';
    
    return {
      level: level,
      score: severityScore,
      factors: severityFactors
    };
  }

  generateForecastActions(periods) {
    const actions = [];
    
    periods.slice(0, 3).forEach(period => {
      const description = period.detailedForecast.toLowerCase();
      
      if (description.includes('storm')) {
        actions.push('Secure outdoor objects and equipment');
      }
      if (description.includes('flood')) {
        actions.push('Avoid low-lying areas and underpasses');
      }
      if (period.temperature > 100) {
        actions.push('Implement heat safety protocols');
      }
      if (period.temperature < 32) {
        actions.push('Protect pipes and outdoor plants from freezing');
      }
    });
    
    return [...new Set(actions)]; // Remove duplicates
  }

  generateAlertActions(alerts) {
    const actions = [];
    
    alerts.forEach(alert => {
      const severity = alert.properties.severity;
      const event = alert.properties.event.toLowerCase();
      
      if (severity === 'Extreme' || severity === 'Severe') {
        actions.push('Take immediate protective action');
      }
      
      if (event.includes('tornado')) {
        actions.push('Seek sturdy shelter immediately');
      }
      if (event.includes('hurricane')) {
        actions.push('Follow evacuation orders if issued');
      }
      if (event.includes('flood')) {
        actions.push('Move to higher ground');
      }
      
      if (alert.properties.instruction) {
        actions.push(`Official guidance: ${alert.properties.instruction.substring(0, 100)}...`);
      }
    });
    
    return [...new Set(actions)];
  }

  convertCelsiusToFahrenheit(celsius) {
    return celsius ? Math.round((celsius * 9/5) + 32) : null;
  }

  convertMpsToMph(mps) {
    return mps ? Math.round(mps * 2.237) : null;
  }

  convertMetersToMiles(meters) {
    return meters ? Math.round(meters * 0.000621371) : null;
  }
}

module.exports = ForecastAgent;