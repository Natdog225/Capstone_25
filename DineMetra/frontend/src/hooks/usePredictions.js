import { useState, useCallback, useEffect } from 'react';
import { dinemetraAPI } from '../services/dinemetraService';

const PREDICTION_CONFIG = {
  waitTime: {
    fn: (partySize) => dinemetraAPI.predictWaitTimeEnhanced(partySize),
    defaultArgs: [4]
  },
  busyness: {
    fn: () => dinemetraAPI.predictBusynessEnhanced(),
    defaultArgs: []
  },
  sales: {
    fn: (itemId, dateRange, itemName, category) => 
      dinemetraAPI.predictSalesEnhanced(itemId, dateRange, itemName, category),
    defaultArgs: [101, null, 'Burger Special', 'Entrees']
  }
};

export const usePredictions = () => {
  const [predictions, setPredictions] = useState({
    waitTime: null,
    busyness: null,
    sales: null
  });

  const [loading, setLoading] = useState({
    waitTime: false,
    busyness: false,
    sales: false
  });

  const [errors, setErrors] = useState({
    waitTime: null,
    busyness: null,
    sales: null
  });

  const refreshPrediction = useCallback(async (type, ...args) => {
    const config = PREDICTION_CONFIG[type];
    if (!config) {
      console.error(`Unknown prediction type: ${type}`);
      setErrors(prev => ({ ...prev, [type]: 'Invalid prediction type' }));
      return;
    }

    setLoading(prev => ({ ...prev, [type]: true }));
    setErrors(prev => ({ ...prev, [type]: null }));

    try {
      console.log(`Calling ${type} with args:`, args);
      const result = await config.fn(...(args.length ? args : config.defaultArgs));
      
      console.log(`Raw ${type} result:`, result);
      
      if (result && typeof result === 'object') {
        setPredictions(prev => ({ ...prev, [type]: result }));
      } else if (typeof result === 'string') {
        // Handle string responses
        try {
          const parsed = JSON.parse(result);
          setPredictions(prev => ({ ...prev, [type]: parsed }));
        } catch {
          setPredictions(prev => ({ ...prev, [type]: { message: result } }));
        }
      } else {
        throw new Error('Invalid response format from API');
      }
    } catch (error) {
      const message = error.response?.data?.detail?.[0]?.msg || 
                      error.response?.data?.message || 
                      error.message || 
                      'Unknown API error';
      console.error(`Prediction error (${type}):`, error);
      setErrors(prev => ({ ...prev, [type]: message }));
    } finally {
      // FIXED: Added missing closing parenthesis here
      setLoading(prev => ({ ...prev, [type]: false }));
    }
  }, []);

  const refreshAll = useCallback(async () => {
    await Promise.allSettled([
      refreshPrediction('waitTime'),
      refreshPrediction('busyness'),
      refreshPrediction('sales')
    ]);
  }, [refreshPrediction]);

  // Auto-refresh on mount
  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  return {
    predictions,
    loading,
    errors,
    refreshPrediction,
    refreshAll
  };
};