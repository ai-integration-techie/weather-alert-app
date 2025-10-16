const { Agent } = require('@google-cloud/agent-toolkit');
const { BigQuery } = require('@google-cloud/bigquery');
const config = require('../config/environment');

class DataAgent extends Agent {
  constructor() {
    super({
      name: 'data-agent',
      description: 'Queries BigQuery NOAA datasets for historical weather data and analytics',
      projectId: config.agent.projectId,
      region: config.agent.region
    });
    
    this.bigquery = new BigQuery({
      projectId: config.projectId,
      location: config.bigquery.location
    });
    
    this.capabilities = [
      'historical_data_analysis',
      'storm_track_queries',
      'flood_record_analysis',
      'temperature_extremes',
      'precipitation_patterns'
    ];
  }

  async initialize() {
    await super.initialize();
    
    this.tools = [
      {
        name: 'query_historical_storms',
        description: 'Query historical storm data from NOAA datasets',
        parameters: {
          type: 'object',
          properties: {
            location: { type: 'string' },
            storm_type: { type: 'string', enum: ['hurricane', 'tornado', 'thunderstorm'] },
            years_back: { type: 'number', default: 10 }
          }
        }
      },
      {
        name: 'analyze_flood_risk',
        description: 'Analyze historical flood data for specific river basins',
        parameters: {
          type: 'object',
          properties: {
            river_basin: { type: 'string' },
            rainfall_rate: { type: 'number' },
            time_period: { type: 'string' }
          }
        }
      },
      {
        name: 'get_temperature_extremes',
        description: 'Get historical temperature extremes for heat wave analysis',
        parameters: {
          type: 'object',
          properties: {
            location: { type: 'string' },
            duration_hours: { type: 'number', default: 48 }
          }
        }
      }
    ];
  }

  async processRequest(query, context) {
    try {
      const queryType = this.classifyQuery(query);
      
      switch (queryType) {
        case 'flood_analysis':
          return await this.handleFloodAnalysis(query, context);
        case 'storm_history':
          return await this.handleStormHistory(query, context);
        case 'temperature_analysis':
          return await this.handleTemperatureAnalysis(query, context);
        default:
          return await this.handleGeneralDataQuery(query, context);
      }
    } catch (error) {
      console.error('Data Agent error:', error);
      return {
        error: true,
        message: 'Unable to retrieve historical data at this time',
        timestamp: new Date().toISOString()
      };
    }
  }

  classifyQuery(query) {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('flood') || lowerQuery.includes('rainfall') || lowerQuery.includes('river')) {
      return 'flood_analysis';
    }
    if (lowerQuery.includes('hurricane') || lowerQuery.includes('storm') || lowerQuery.includes('tornado')) {
      return 'storm_history';
    }
    if (lowerQuery.includes('heat') || lowerQuery.includes('temperature') || lowerQuery.includes('cooling')) {
      return 'temperature_analysis';
    }
    
    return 'general';
  }

  async handleFloodAnalysis(query, context) {
    const sqlQuery = `
      SELECT 
        year,
        month,
        max_precipitation_mm,
        flood_events,
        affected_population
      FROM \`bigquery-public-data.noaa_historic_severe_storms.storms_*\`
      WHERE REGEXP_EXTRACT(_TABLE_SUFFIX, r'[0-9]+') BETWEEN '2010' AND '2023'
        AND event_type = 'Flood'
        AND state = @state
      ORDER BY max_precipitation_mm DESC
      LIMIT 50
    `;

    const options = {
      query: sqlQuery,
      params: {
        state: this.extractLocationFromQuery(query) || 'TX'
      }
    };

    const [rows] = await this.bigquery.query(options);
    
    return {
      summary: `Found ${rows.length} historical flood events in the specified area`,
      details: rows.map(row => ({
        date: `${row.year}-${row.month}`,
        precipitation: row.max_precipitation_mm,
        events: row.flood_events,
        population_affected: row.affected_population
      })),
      analysis: this.analyzeFloodData(rows),
      sources: ['NOAA Historic Severe Storms Dataset'],
      timestamp: new Date().toISOString()
    };
  }

  async handleStormHistory(query, context) {
    const sqlQuery = `
      SELECT 
        name,
        iso_time,
        lat,
        lon,
        wind_kts,
        pressure,
        category,
        dist2land
      FROM \`bigquery-public-data.noaa_hurricanes.hurricanes\`
      WHERE season >= EXTRACT(YEAR FROM DATE_SUB(CURRENT_DATE(), INTERVAL 10 YEAR))
        AND category >= 3
        AND dist2land <= 100
      ORDER BY wind_kts DESC
      LIMIT 20
    `;

    const [rows] = await this.bigquery.query(sqlQuery);
    
    return {
      summary: `Found ${rows.length} major hurricanes (Category 3+) within 100 miles of land in the last 10 years`,
      details: rows.map(row => ({
        name: row.name,
        date: row.iso_time,
        location: [row.lat, row.lon],
        wind_speed: row.wind_kts,
        pressure: row.pressure,
        category: row.category,
        distance_to_land: row.dist2land
      })),
      emergency_actions: this.generateStormActions(rows),
      sources: ['NOAA Hurricane Database'],
      timestamp: new Date().toISOString()
    };
  }

  async handleTemperatureAnalysis(query, context) {
    const sqlQuery = `
      SELECT 
        date,
        temperature_max,
        temperature_min,
        heat_index,
        state
      FROM \`bigquery-public-data.noaa_gsod.gsod*\`
      WHERE _TABLE_SUFFIX >= FORMAT_DATE('%Y', DATE_SUB(CURRENT_DATE(), INTERVAL 5 YEAR))
        AND temperature_max > 100
        AND state = @state
      ORDER BY temperature_max DESC
      LIMIT 30
    `;

    const options = {
      query: sqlQuery,
      params: {
        state: this.extractLocationFromQuery(query) || 'TX'
      }
    };

    const [rows] = await this.bigquery.query(options);
    
    return {
      summary: `Found ${rows.length} extreme heat days (>100°F) in the last 5 years`,
      details: rows.map(row => ({
        date: row.date,
        max_temp: row.temperature_max,
        min_temp: row.temperature_min,
        heat_index: row.heat_index,
        state: row.state
      })),
      recommendations: this.generateHeatRecommendations(rows),
      sources: ['NOAA Global Summary of the Day'],
      timestamp: new Date().toISOString()
    };
  }

  async handleGeneralDataQuery(query, context) {
    return {
      summary: 'General weather data available',
      details: ['Access to NOAA historical datasets', 'Storm tracking data', 'Temperature records'],
      capabilities: this.capabilities,
      sources: ['NOAA BigQuery Public Datasets'],
      timestamp: new Date().toISOString()
    };
  }

  extractLocationFromQuery(query) {
    const stateRegex = /\b([A-Z]{2})\b/g;
    const match = query.match(stateRegex);
    return match ? match[0] : null;
  }

  analyzeFloodData(data) {
    if (data.length === 0) return { risk_level: 'low', probability: 0 };
    
    const avgPrecipitation = data.reduce((sum, row) => sum + row.max_precipitation_mm, 0) / data.length;
    const maxPrecipitation = Math.max(...data.map(row => row.max_precipitation_mm));
    
    let riskLevel = 'low';
    let probability = 0;
    
    if (avgPrecipitation > 50) {
      riskLevel = 'high';
      probability = 0.7;
    } else if (avgPrecipitation > 25) {
      riskLevel = 'medium';
      probability = 0.4;
    } else {
      probability = 0.2;
    }
    
    return {
      risk_level: riskLevel,
      probability: probability,
      avg_precipitation: avgPrecipitation,
      max_precipitation: maxPrecipitation,
      historical_events: data.length
    };
  }

  generateStormActions(stormData) {
    const actions = [];
    
    if (stormData.some(storm => storm.category >= 4)) {
      actions.push('Immediate evacuation recommended for coastal areas');
      actions.push('Secure or relocate outdoor equipment and vehicles');
    }
    
    actions.push('Monitor official weather channels for updates');
    actions.push('Ensure emergency supplies are readily available');
    actions.push('Review evacuation routes and shelter locations');
    
    return actions;
  }

  generateHeatRecommendations(heatData) {
    const recommendations = [];
    
    if (heatData.some(day => day.temperature_max > 110)) {
      recommendations.push('Establish cooling centers for vulnerable populations');
      recommendations.push('Issue heat emergency alerts');
    }
    
    recommendations.push('Increase hydration reminders');
    recommendations.push('Limit outdoor activities during peak hours');
    recommendations.push('Check on elderly and vulnerable community members');
    
    return recommendations;
  }
}

module.exports = DataAgent;