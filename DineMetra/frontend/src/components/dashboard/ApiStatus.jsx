import React, { useState, useEffect } from 'react';
import { Activity, AlertCircle, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import { dinemetraAPI } from '../../services/dinemetraService';
import './CSS/ApiStatus.css';

const ApiStatus = () => {
  const [status, setStatus] = useState('checking'); // 'checking', 'healthy', 'degraded', 'error'
  const [performance, setPerformance] = useState(null);
  const [lastChecked, setLastChecked] = useState(null);
  const [loading, setLoading] = useState(false);

  const checkHealth = async () => {
    setLoading(true);
    try {
      const data = await dinemetraAPI.getModelPerformance();
      console.log('API Health Check:', data);
      
      // Determine overall status
      const models = ['waitTime', 'busyness', 'itemSales'];
      const statuses = models.map(model => data[model]?.status);
      
      if (statuses.every(s => s === 'healthy')) {
        setStatus('healthy');
      } else if (statuses.some(s => s === 'unhealthy')) {
        setStatus('error');
      } else {
        setStatus('degraded');
      }
      
      setPerformance(data);
      setLastChecked(new Date());
    } catch (error) {
      console.error('Health check failed:', error);
      setStatus('error');
      setPerformance(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Check on mount
    checkHealth();
    
    // Check every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = () => {
    switch(status) {
      case 'healthy':
        return <CheckCircle size={16} className="status-icon healthy" />;
      case 'degraded':
        return <AlertCircle size={16} className="status-icon warning" />;
      case 'error':
        return <XCircle size={16} className="status-icon error" />;
      default:
        return <Activity size={16} className="status-icon checking" />;
    }
  };

  const getStatusText = () => {
    switch(status) {
      case 'healthy':
        return 'All Systems Operational';
      case 'degraded':
        return 'Some Models Degraded';
      case 'error':
        return 'API Connection Failed';
      default:
        return 'Checking Status...';
    }
  };

  const formatLastChecked = () => {
    if (!lastChecked) return '';
    const now = new Date();
    const diff = Math.floor((now - lastChecked) / 1000);
    if (diff < 60) return `(${diff}s ago)`;
    if (diff < 3600) return `(${Math.floor(diff / 60)}m ago)`;
    return '';
  };

  return (
    <div className="api-status-widget" onClick={checkHealth} title="Click to refresh">
      {loading ? (
        <RefreshCw size={16} className="status-icon spinning" />
      ) : (
        getStatusIcon()
      )}
      <span className={`status-text ${status}`}>
        {getStatusText()}
      </span>
      <span className="last-checked">
        {formatLastChecked()}
      </span>
      
      {performance && (
        <div className="health-details">
          <div className="model-status">
            <span className="model-name">Wait Time:</span>
            <span className={`model-value ${performance.waitTime?.status}`}>
              {performance.waitTime?.status}
            </span>
          </div>
          <div className="model-status">
            <span className="model-name">Busyness:</span>
            <span className={`model-value ${performance.busyness?.status}`}>
              {performance.busyness?.status}
            </span>
          </div>
          <div className="model-status">
            <span className="model-name">Item Sales:</span>
            <span className={`model-value ${performance.itemSales?.status}`}>
              {performance.itemSales?.status}
            </span>
          </div>
          <div className="last-trained">
            Last trained: {new Date(performance.last_trained).toLocaleString()}
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiStatus;