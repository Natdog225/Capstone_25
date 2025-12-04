import React from 'react';
import './MetricCard.css';

const MetricCard = ({ title, value, loading, icon }) => {
  return (
    <div className="metric-card fade-in">
      <div className="metric-icon">{icon}</div>
      <div className="metric-content">
        <h3 className="metric-label">{title}</h3>
        {loading ? (
          <div className="loading-spinner">...</div>
        ) : (
          <p className="metric-value">{value}</p>
        )}
      </div>
    </div>
  );
};

export default MetricCard;