/**
 * Custom React hook for fetching API data with loading and error states
 */
import { useState, useEffect } from 'react';

const useApiData = (apiCall, dependencies = [], options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const {
    immediate = true,
    onSuccess,
    onError,
    defaultValue = null
  } = options;

  const fetchData = async (...args) => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiCall(...args);
      setData(result);
      if (onSuccess) onSuccess(result);
      return result;
    } catch (err) {
      console.error('API Error:', err);
      setError(err.message || 'An error occurred');
      setData(defaultValue);
      if (onError) onError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (immediate && dependencies.every(dep => dep !== undefined)) {
      fetchData(...dependencies);
    } else if (!immediate) {
      setLoading(false);
    }
  }, dependencies);

  const refetch = (...args) => {
    return fetchData(...(args.length ? args : dependencies));
  };

  return { data, loading, error, refetch };
};

export default useApiData;

// Specialized hooks for common API calls
export const useBusynessPrediction = (date, hoursAhead = 24) => {
  return useApiData(
    async () => {
      const { default: api } = await import('../services/api');
      return api.predictHourlyBusyness(date, hoursAhead);
    },
    [date, hoursAhead],
    { immediate: !!date }
  );
};

export const useMenuItems = (category = null, isActive = true) => {
  return useApiData(
    async () => {
      const { default: api } = await import('../services/api');
      return api.getMenuItems(category, isActive);
    },
    [category, isActive]
  );
};

export const useDailyAnalytics = (startDate, endDate) => {
  return useApiData(
    async () => {
      const { default: api } = await import('../services/api');
      return api.getDailyAnalytics(startDate, endDate);
    },
    [startDate, endDate],
    { immediate: !!(startDate && endDate) }
  );
};

export const useWeeklyForecast = () => {
  return useApiData(
    async () => {
      const { default: api } = await import('../services/api');
      return api.predictWeeklyBusyness();
    },
    []
  );
};