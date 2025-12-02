import React, { useState, useEffect } from 'react';
import { 
  ShoppingCart, 
  Wine, 
  Beer, 
  Users, 
  TrendingUp,
  DollarSign,
  Calendar
} from 'lucide-react';
import { dinemetraAPI } from '../../services/dinemetraService';
import './CSS/Metricsgrid.css';

const iconMap = {
  ShoppingCart: ShoppingCart,
  Wine: Wine,
  Beer: Beer,
  Users: Users,
  TrendingUp: TrendingUp,
  DollarSign: DollarSign
};

const MetricsGrid = ({ dateRange, onPeriodChange }) => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        // Pass the date range to the API
        const data = await dinemetraAPI.getMetrics(dateRange.startDate, dateRange.endDate);
        setMetrics(data);
        setError(null);
      } catch (err) {
        console.error('Failed to load metrics:', err);
        setError('Failed to load metrics');
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, [dateRange]);

  if (loading) {
    return (
      <div className="metrics-section">
        <div className="loading-grid">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="metric-card card loading">
              <div className="loading-spinner">Loading...</div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="metrics-section">
        <div className="error-message">
          <p>⚠️ {error || 'Failed to load metrics'}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  const { categories = [], summaries = [], purchasing = [] } = metrics;

  return (
    <div className="metrics-section">
        <div className="metrics-header">
        <h2 className="section-title">Sales Metrics</h2>
        </div>
      <div className="metrics-grid">
        {(categories || []).map((metric) => {
          const IconComponent = iconMap[metric.icon] || ShoppingCart;
          return (
            <div key={metric.id} className="metric-card card">
              <div className="metric-card-header">
                <IconComponent size={20} className="metric-icon" />
                <h3 className="metric-title">{metric.title}</h3>
              </div>
              <div className="metric-items">
                {metric.items.map((item, index) => (
                  <div key={index} className="metric-item">
                    <span className="item-name">{item.name}</span>
                    <div className="item-value-wrapper">
                      <span className="item-value">{item.value}</span>
                      {item.trend === 'up' && <span className="trend-indicator up">↑</span>}
                      {item.trend === 'down' && <span className="trend-indicator down">↓</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      <div className="secondary-metrics">
        {(summaries || []).map((metric) => {
          const IconComponent = iconMap[metric.icon] || Users;
          return (
            <div key={metric.id} className={`metric-highlight card ${metric.status}`}>
              <div className="highlight-header">
                <IconComponent size={20} className="metric-icon" />
                <h3 className="metric-title">{metric.title}</h3>
              </div>
              <div className="highlight-value">{metric.percentage}</div>
              {metric.target && (
                <div className="highlight-target">Target: {metric.target}</div>
              )}
              {metric.variance && (
                <div className="highlight-variance">{metric.variance}</div>
              )}
              <div className="highlight-details">{metric.details}</div>
            </div>
          );
        })}
      </div>

      {purchasing.length > 0 && (
        <div className="purchasing-section card">
          <h3 className="section-title">Purchasing Estimates</h3>
          <div className="purchasing-grid">
            {purchasing.map((item, index) => (
              <div key={index} className="purchasing-item">
                <div className="purchasing-info">
                  <span className="purchasing-name">{item.item}</span>
                  <span className="purchasing-estimate">{item.estimate}</span>
                </div>
                <span className={`purchasing-status ${item.status.toLowerCase().replace(/\s+/g, '-')}`}>
                  {item.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MetricsGrid;