import api from './api';

export const dinemetraAPI = {
  // Health check
  async healthCheck() {
    try {
      const { data } = await api.get('/');
      return data;
    } catch (error) {
      console.warn('API health check failed:', error.message);
      return null;
    }
  },

  // Predict wait time
  async predictWaitTime(partySize, timestamp = null, currentOccupancy = 50) {
    const requestBody = {
      party_size: partySize,
      timestamp: timestamp || new Date().toISOString(),
      current_occupancy: currentOccupancy
    };
    
    const { data } = await api.post('/api/predictions/wait-time', requestBody);
    return data;
  },

  // Predict busyness (Slow, Moderate, Peak)
  async predictBusyness(timestamp = null, weatherCondition = null) {
    const requestBody = {
      timestamp: timestamp || new Date().toISOString(),
      weather_condition: weatherCondition
    };
    
    const { data } = await api.post('/api/predictions/busyness', requestBody);
    return data;
  },

  // Predict sales for specific menu items
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