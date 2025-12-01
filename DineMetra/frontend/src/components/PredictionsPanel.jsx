import React, { useState } from 'react';
import { Clock, TrendingUp, ShoppingCart } from 'lucide-react';
import { dinemetraAPI } from '../services/dinemetraService';
import './dashboard/CSS/PredictionPanel.css';

const PredictionsPanel = () => {
  const [waitTime, setWaitTime] = useState(null);
  const [busyness, setBusyness] = useState(null);
  const [salesPrediction, setSalesPrediction] = useState(null);
  const [loading, setLoading] = useState({ waitTime: false, busyness: false, sales: false });

  const handlePredictWaitTime = async () => {
    setLoading(prev => ({ ...prev, waitTime: true }));
    try {
      const result = await dinemetraAPI.predictWaitTime(4);
      setWaitTime(result);
    } catch (error) {
      setWaitTime({ error: error.message });
    } finally {
      setLoading(prev => ({ ...prev, waitTime: false }));
    }
  };

  const handlePredictBusyness = async () => {
    setLoading(prev => ({ ...prev, busyness: true }));
    try {
      const result = await dinemetraAPI.predictBusyness();
      setBusyness(result);
    } catch (error) {
      setBusyness({ error: error.message });
    } finally {
      setLoading(prev => ({ ...prev, busyness: false }));
    }
  };

  const handlePredictSales = async () => {
    setLoading(prev => ({ ...prev, sales: true }));
    try {
      const result = await dinemetraAPI.predictSales(101, null, 'Burger Special', 'Entrees');
      console.log('API returned:', result); // Debug what the API actually returns
      setSalesPrediction(result);
    } catch (error) {
      setSalesPrediction({ error: error.message });
    } finally {
      setLoading(prev => ({ ...prev, sales: false }));
    }
  };

  const handleRefreshAll = async () => {
    await Promise.all([
      handlePredictWaitTime(),
      handlePredictBusyness(),
      handlePredictSales()
    ]);
  };

  return (
    <div className="predictions-panel card fade-in">
      <div className="panel-header">
        <h2 className="section-title">AI Predictions</h2>
        <button 
          onClick={handleRefreshAll} 
          className="refresh-btn"
          disabled={loading.waitTime || loading.busyness || loading.sales}
        >
          {loading.waitTime || loading.busyness || loading.sales ? 'Loading...' : '🔄 Refresh Predictions'}
        </button>
      </div>

      <div className="predictions-grid">
        {/* Wait Time Prediction */}
        <div className="prediction-card">
          <div className="card-header">
            <Clock size={24} className="icon" />
            <h3>Wait Time</h3>
          </div>
          <button onClick={handlePredictWaitTime} disabled={loading.waitTime}>
            {loading.waitTime ? 'Predicting...' : 'Predict for Party of 4'}
          </button>
          {waitTime && !waitTime.error && (
            <div className="result">
              <p className="value">{waitTime.predicted_wait_minutes} min</p>
              <p className="confidence">Confidence: {(waitTime.confidence * 100).toFixed(1)}%</p>
              <details>
                <summary>Factors</summary>
                <pre>{JSON.stringify(waitTime.factors, null, 2)}</pre>
              </details>
            </div>
          )}
          {waitTime?.error && <p className="error">{waitTime.error}</p>}
        </div>

        {/* Busyness Prediction */}
        <div className="prediction-card">
          <div className="card-header">
            <TrendingUp size={24} className="icon" />
            <h3>Busyness Level</h3>
          </div>
          <button onClick={handlePredictBusyness} disabled={loading.busyness}>
            {loading.busyness ? 'Analyzing...' : 'Predict Now'}
          </button>
          {busyness && !busyness.error && (
            <div className="result">
              {/* Show the raw response structure first to understand it */}
              <pre>{JSON.stringify(busyness, null, 2)}</pre>
            </div>
          )}
          {busyness?.error && <p className="error">{busyness.error}</p>}
        </div>

        {/* Sales Prediction */}
        <div className="prediction-card">
          <div className="card-header">
            <ShoppingCart size={24} className="icon" />
            <h3>Sales Forecast</h3>
          </div>
          <button onClick={handlePredictSales} disabled={loading.sales}>
            {loading.sales ? 'Forecasting...' : 'Predict Burger Sales'}
          </button>
          {salesPrediction && !salesPrediction.error && (
            <div className="result">
              {/* FIX: Access the correct property */}
              <p className="value">{salesPrediction.predicted_quantity}</p>
              <p className="label">predicted units</p>
              <p className="confidence">Confidence: {(salesPrediction.confidence * 100).toFixed(1)}%</p>
            </div>
          )}
          {salesPrediction?.error && <p className="error">{salesPrediction.error}</p>}
        </div>
      </div>
    </div>
  );
};

export default PredictionsPanel;