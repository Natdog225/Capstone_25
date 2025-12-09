import api from './api';

// TypeScript-style JSDoc for type safety (optional but recommended)

/**
 * @typedef {Object} TrendData
 * @property {Array} daily_data
 * @property {string} start_date
 * @property {string} end_date
 * @property {number} peak_wait_time
 * @property {number} avg_daily_sales
 * @property {string} busiest_day
 * @property {string} trend_direction
 */

/**
 * @typedef {Object} HistoricalComparison
 * @property {string} date
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
    const { data } = await api.get('/api/monitoring/model-performance');
    return data;
  },

  async dashboardHealth() {
    const { data } = await api.get('/api/dashboard/health');
    return data;
  },

  async getModelPerformance() {
    const { data } = await api.get('/api/monitoring/model-performance');
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

 // Cache for trends data to inform mocks
  _cachedTrends: null,

  // ===== HISTORICAL COMPARISON WITH SMART MOCKING =====
  
  async compareWaitTimes(date = null) {
    try {
      // Try real API first
      const response = await api.get('/api/historical/compare/wait-times', {
        params: date ? { date } : {}
      });
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        // Use real trends data to generate realistic comparison
        const trends = await this.getDailyTrends(30, date);
        return this._generateMockFromTrends(trends, 'wait_time', date);
      }
      throw error;
    }
  },

  async compareSales(date = null) {
    try {
      const response = await api.get('/api/historical/compare/sales', {
        params: date ? { date } : {}
      });
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        const trends = await this.getDailyTrends(30, date);
        return this._generateMockFromTrends(trends, 'sales', date);
      }
      throw error;
    }
  },

  async compareBusyness(date = null) {
    try {
      const response = await api.get('/api/historical/compare/busyness', {
        params: date ? { date } : {}
      });
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        const trends = await this.getDailyTrends(30, date);
        return this._generateMockFromTrends(trends, 'busyness', date);
      }
      throw error;
    }
  },

  // ✅ WORKING ENDPOINT - Use this directly
  async getDailyTrends(days = 30, endDate = null) {
    const params = { days };
    if (endDate) params.end_date = endDate;
    const response = await api.get('/api/historical/trends/daily', { params });
    // Cache it for mock generation
    this._cachedTrends = response.data;
    return response.data;
  },

  // Generate realistic mock data based on actual trends
  _generateMockFromTrends(trends, type, selectedDate) {
    if (!trends?.daily_data?.length) {
      return this._getDefaultMock(type);
    }

    // Find the selected date or closest match
    const targetDate = selectedDate || new Date().toISOString().split('T')[0];
    const selectedIndex = trends.daily_data.findIndex(d => d.date === targetDate);
    
    // Use selected date or latest data
    const todayData = trends.daily_data[selectedIndex] || trends.daily_data[trends.daily_data.length - 1];
    
    // Calculate week-over-week using real data
    const weekAgoIndex = Math.max(0, (selectedIndex >= 0 ? selectedIndex : trends.daily_data.length - 1) - 7);
    const weekAgoData = trends.daily_data[weekAgoIndex] || todayData;
    
    // Calculate year-over-year (approximate using 52 weeks ago)
    const yearAgoIndex = Math.max(0, (selectedIndex >= 0 ? selectedIndex : trends.daily_data.length - 1) - 364);
    const yearAgoData = trends.daily_data[yearAgoIndex] || todayData;

    const calculateChange = (current, previous) => {
      if (!previous || previous === 0) return 0;
      return ((current - previous) / previous) * 100;
    };

    // Build realistic comparison based on actual daily data
    const templates = {
      wait_time: {
        today: { average_minutes: todayData.wait_time, count: todayData.order_count },
        last_week: { 
          average_minutes: weekAgoData.wait_time, 
          count: weekAgoData.order_count,
          change_percent: calculateChange(todayData.wait_time, weekAgoData.wait_time)
        },
        last_year: { 
          average_minutes: yearAgoData.wait_time, 
          count: yearAgoData.order_count,
          change_percent: calculateChange(todayData.wait_time, yearAgoData.wait_time)
        },
        insight: `Wait times ${todayData.wait_time > weekAgoData.wait_time ? 'up' : 'down'} from last week`
      },
      sales: {
        today: { total: todayData.sales, order_count: todayData.order_count },
        last_week: { 
          total: weekAgoData.sales, 
          order_count: weekAgoData.order_count,
          change_percent: calculateChange(todayData.sales, weekAgoData.sales)
        },
        last_year: { 
          total: yearAgoData.sales, 
          order_count: yearAgoData.order_count,
          change_percent: calculateChange(todayData.sales, yearAgoData.sales)
        },
        insight: `Sales ${todayData.sales > weekAgoData.sales ? 'beating' : 'trailing'} last week`
      },
      busyness: {
        today: { orders_per_hour: Math.round(todayData.order_count / 24), total_orders: todayData.order_count },
        last_week: { 
          orders_per_hour: Math.round(weekAgoData.order_count / 24), 
          total_orders: weekAgoData.order_count,
          change_percent: calculateChange(todayData.order_count, weekAgoData.order_count)
        },
        last_year: { 
          orders_per_hour: Math.round(yearAgoData.order_count / 24), 
          total_orders: yearAgoData.order_count,
          change_percent: calculateChange(todayData.order_count, yearAgoData.order_count)
        },
        insight: `Busyness ${todayData.order_count > weekAgoData.order_count ? 'higher' : 'lower'} than last week`
      }
    };

    return templates[type] || templates.wait_time;
  },

  _getDefaultMock(type) {
    const defaults = {
      wait_time: {
        today: { average_minutes: 24.5, count: 79 },
        last_week: { average_minutes: 25.2, count: 76, change_percent: -2.8 },
        last_year: { average_minutes: 28.0, count: 65, change_percent: -12.5 },
        insight: "Wait times trending downward"
      },
      sales: {
        today: { total: 2859, order_count: 79 },
        last_week: { total: 2750, order_count: 76, change_percent: 4.0 },
        last_year: { total: 2400, order_count: 65, change_percent: 19.1 },
        insight: "Sales up 4% from last week"
      },
      busyness: {
        today: { orders_per_hour: 12, total_orders: 79 },
        last_week: { orders_per_hour: 11.5, total_orders: 76, change_percent: 4.3 },
        last_year: { orders_per_hour: 10.2, total_orders: 65, change_percent: 17.6 },
        insight: "Busyness increasing but manageable"
      }
    };
    return defaults[type] || defaults.wait_time;
  },

  async getHistoricalSummary() {
    try {
      const response = await api.get('/api/historical/summary');
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        return {
          orders: { total_records: 2452 },
          wait_times: { total_records: 2452 },
          date_range: { earliest: '2025-05-31', latest: '2025-06-30' }
        };
      }
      throw error;
    }
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