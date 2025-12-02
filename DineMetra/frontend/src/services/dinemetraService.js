import api from './api';

// TypeScript-style JSDoc for type safety (optional but recommended)

/**
 * @typedef {Object} Highlight
 * @property {number} id
 * @property {string} title
 * @property {string} icon
 * @property {string} color
 * @property {string} details
 * @property {string} subDetails
 * @property {'high'|'medium'|'low'} importance
 */

/**
 * @typedef {Object} SalesChartData
 * @property {string} day
 * @property {number} thisWeek
 * @property {number} pastData
 * @property {number} actual
 */

/**
 * @typedef {Object} DashboardData
 * @property {Highlight[]} highlights
 * @property {SalesChartData[]} chartData
 * @property {Object} metrics
 * @property {Object} infoData
 * @property {Object} userProfile
 */

export const dinemetraAPI = {
  // ===== HEALTH & MONITORING =====
  async healthCheck() {
    const { data } = await api.get('/');
    return data;
  },

  async dashboardHealth() {
    const { data } = await api.get('/health');
    return data;
  },

  async getModelPerformance() {
    const { data } = await api.get('/health');
    return data;
  },

  // ===== DASHBOARD DATA (RECOMMENDED: Use single endpoint) =====
  async getCompleteDashboard() {
    const { data } = await api.get('/api/dashboard/dashboard');
    return data;
  },

  // ===== OR: Granular dashboard endpoints =====
  async getHighlights() {
    const { data } = await api.get('/api/dashboard/highlights');
    return data;
  },

    async getSalesChart(startDate, endDate) {
        const response = await api.get('/api/dashboard/sales-chart', {
        params: { start_date: startDate, end_date: endDate }
        });
        // If API returns { data: [...] }, extract it
        return response.data.data || response.data;
    },


async getMetrics(startDate, endDate) {
  const response = await api.get('/api/dashboard/metrics', {
    params: { start_date: startDate, end_date: endDate }
  });
  return response.data.data || response.data;
},

  async getInfoSections() {
    const { data } = await api.get('/api/dashboard/info-sections');
    return data;
  },

  async getUserProfile() {
    const { data } = await api.get('/api/dashboard/user-profile');
    return data;
  },

  // ===== PREDICTIONS (ENHANCED - RECOMMENDED) =====
  async predictWaitTimeEnhanced(partySize, timestamp = null, currentOccupancy = 50, testWeather = null) {
    const requestBody = {
      party_size: partySize,
      current_occupancy: currentOccupancy,
      timestamp: timestamp || new Date().toISOString(),
      test_weather_condition: testWeather
    };
    
    const { data } = await api.post('/api/predictions/wait-time-enhanced', requestBody);
    return data;
  },

  async predictBusynessEnhanced(timestamp = null, weather = null) {
    const requestBody = {
      timestamp: timestamp || new Date().toISOString(),
      weather_condition: weather
    };
    
    const { data } = await api.post('/api/predictions/busyness-enhanced', requestBody);
    return data;
  },

  async predictSalesEnhanced(itemId, date = null, itemName = "Unknown", category = "Entrees") {
    const requestBody = {
      item_id: itemId,
      date: date || new Date().toISOString(),
      item_name: itemName,
      category: category
    };
    
    const { data } = await api.post('/api/predictions/sales-enhanced', requestBody);
    return data;
  },

  // ===== HISTORICAL COMPARISON ENDPOINTS =====
async compareWaitTimes(date = null) {
  const { data } = await api.get('/api/historical/compare/wait-times', {
    params: { date }
  });
  return data;
},

async compareSales(date = null) {
  const { data } = await api.get('/api/historical/compare/sales', {
    params: { date }
  });
  return data;
},

async compareBusyness(date = null) {
  const { data } = await api.get('/api/historical/compare/busyness', {
    params: { date }
  });
  return data;
},

async compareAllHistorical(date = null) {
  const { data } = await api.get('/api/historical/compare/all', {
    params: { date }
  });
  return data;
},

async getWeeklyTrends(weeks = 4) {
  const { data } = await api.get('/api/historical/trends/weekly', {
    params: { weeks }
  });
  return data;
},

async getHistoricalSummary() {
  const { data } = await api.get('/api/historical/summary');
  return data;
},

  // ===== DASHBOARD PREDICTIONS (GET versions) =====
  async getBusynessPrediction(timestamp = null) {
    const params = timestamp ? { timestamp } : {};
    const { data } = await api.get('/api/dashboard/predictions/busyness-enhanced', { params });
    return data;
  },

  async getAllEvents(days = 60) {
  const { data } = await api.get('/api/dashboard/events', {
    params: { 
      days: days,
      exclude_keywords: 'SKY CLUB,SUITES,UPCHARGE,CLUB SEATS'
    }
  });
  return data;
},
  async getSalesPrediction(itemId, targetDate = null, itemName = "Unknown", category = "Entrees") {
    const params = {
      item_id: itemId,
      item_name: itemName,
      category: category
    };
    if (targetDate) params.target_date = targetDate;
    
    const { data } = await api.get('/api/dashboard/predictions/sales-enhanced', { params });
    return data;
  },

  // ===== FEEDBACK =====
  async submitFeedback(predictionType, predictionId, actualValue, notes = null) {
    const params = {
      prediction_type: predictionType,
      prediction_id: predictionId,
      actual_value: actualValue,
    };
    if (notes) params.notes = notes;
    
    const { data } = await api.get('/api/dashboard/feedback', { params });
    return data;
  },

  // ===== LEGACY (Original predictions - kept for backward compatibility) =====
  async predictWaitTime(partySize, timestamp = null, currentOccupancy = 50) {
    const requestBody = {
      party_size: partySize,
      timestamp: timestamp || new Date().toISOString(),
      current_occupancy: currentOccupancy
    };
    
    const { data } = await api.post('/api/predictions/wait-time', requestBody);
    return data;
  },

  async predictBusyness(timestamp = null, weatherCondition = null) {
    const requestBody = {
      timestamp: timestamp || new Date().toISOString(),
      weather_condition: weatherCondition
    };
    
    const { data } = await api.post('/api/predictions/busyness', requestBody);
    return data;
  },

  async predictSales(itemId, date = null, itemName = "Unknown", category = "Entrees") {
    const requestBody = {
      item_id: itemId,
      date: date || new Date().toISOString(),
      item_name: itemName,
      category: category
    };
    
    const { data } = await api.post('/api/predictions/sales', requestBody);
    return data;
  }
};