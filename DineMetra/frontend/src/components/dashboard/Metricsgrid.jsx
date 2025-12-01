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

const periodOptions = [
  { value: '7-days', label: 'Last 7 Days' },
  { value: '30-days', label: 'Last 30 Days' },
  { value: '90-days', label: 'Last 90 Days' },
  { value: 'this-month', label: 'This Month' },
  { value: 'last-month', label: 'Last Month' }
];

const MetricsGrid = ({ periodRange = '30-days', onPeriodChange }) => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const data = await dinemetraAPI.getMetrics(periodRange);
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
  }, [periodRange]);

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

  // Get current period label for display
  const currentPeriodLabel = periodOptions.find(p => p.value === periodRange)?.label || 'Loading...';

  return (
    <div className="metrics-section">
      <div className="metrics-header">
        <h2 className="section-title">Sales Metrics</h2>
        <div className="period-controls">
          <Calendar size={16} className="calendar-icon" />
          <select 
            value={periodRange} 
            onChange={(e) => onPeriodChange(e.target.value)}
            className="period-selector"
          >
            {periodOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
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