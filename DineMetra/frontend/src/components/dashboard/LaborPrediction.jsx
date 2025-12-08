import React, { useState, useEffect } from 'react';
import { Users } from 'lucide-react';
import { dinemetraAPI } from '../../services/dinemetraService.js';
import './CSS/Infosections.css';

const LaborPrediction = ({ dateRange }) => {
  const [laborData, setLaborData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLaborData = async () => {
      try {
        setLoading(true);
        const data = await dinemetraAPI.getInfoSections();
        console.log('LaborPrediction - Raw API data:', data);
        
        setLaborData(data?.labor || null);
        setError(null);
      } catch (err) {
        console.error('Failed to load labor prediction:', err);
        setError('Failed to load labor data');
      } finally {
        setLoading(false);
      }
    };

    if (dateRange?.startDate && dateRange?.endDate) {
      fetchLaborData();
    }
  }, [dateRange]);

  if (loading) {
    return (
      <div className="info-sections">
        <div className="info-grid">
          <div className="info-card card loading">
            <div className="loading-spinner">Loading...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !laborData) {
    return (
      <div className="info-sections">
        <div className="error-message">
          <p>⚠️ {error || 'Failed to load labor prediction'}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="info-sections">
      <div className="info-grid">
        {/* Labor Prediction */}
        <div className="info-card card labor-card">
          <div className="info-header">
            <Users size={20} className="info-icon labor" />
            <h3 className="info-title">Labor Prediction vs Planned</h3>
          </div>
          <div className="labor-content">
            <div className="labor-metrics">
              <div className="labor-metric">
                <span className="metric-label">Predicted</span>
                <span className="metric-value">{laborData?.predicted || '0'}</span>
                <span className="metric-unit">staff</span>
              </div>
              <div className="labor-metric">
                <span className="metric-label">Planned</span>
                <span className="metric-value">{laborData?.planned || '0'}</span>
                <span className="metric-unit">staff</span>
              </div>
              <div className="labor-metric variance">
                <span className="metric-label">Variance</span>
                <span className="metric-value">{laborData?.variance || '0'}</span>
                <span className="metric-unit">staff</span>
              </div>
            </div>
            <div className="recommendation-box">
              <span className="recommendation-label">AI Recommendation</span>
              <p className="recommendation-text">{laborData?.recommendation || 'No recommendation available'}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LaborPrediction;