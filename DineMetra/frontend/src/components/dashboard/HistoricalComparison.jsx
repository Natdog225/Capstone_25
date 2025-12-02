import React, { useState, useEffect } from 'react';
import { History, Clock, ShoppingCart, Users, AlertCircle, Calendar } from 'lucide-react';
import { dinemetraAPI } from '../../services/dinemetraService.js';
import './CSS/HistoricalComparison.css';

// Utility functions
const getData = (response) => response?.data || {};
const formatValue = (value, fallback = 'N/A') => (value === null || value === undefined || value === '') ? fallback : value;
const formatPercent = (value) => (value === null || value === undefined) ? null : parseFloat(value).toFixed(1);

const HistoricalComparison = ({ dateRange }) => {
  const [historicalData, setHistoricalData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('overview');
  const [trendsWeeks, setTrendsWeeks] = useState(8);

  useEffect(() => {
    if (dateRange?.startDate && dateRange?.endDate) {
      fetchHistoricalData();
    }
  }, [dateRange, trendsWeeks]);

  const fetchHistoricalData = async () => {
    if (!dateRange?.startDate || !dateRange?.endDate) return;
    
    try {
      setLoading(true);
      
      // Fetch data with date parameters from centralized dateRange
      const [waitTimes, sales, busyness, trends, summary] = await Promise.all([
        dinemetraAPI.compareWaitTimes(dateRange.startDate, dateRange.endDate),
        dinemetraAPI.compareSales(dateRange.startDate, dateRange.endDate),
        dinemetraAPI.compareBusyness(dateRange.startDate, dateRange.endDate),
        dinemetraAPI.getWeeklyTrends(trendsWeeks),
        dinemetraAPI.getHistoricalSummary(dateRange.startDate, dateRange.endDate)
      ]);

      setHistoricalData({
        waitTimes: getData(waitTimes),
        sales: getData(sales),
        busyness: getData(busyness),
        trends: getData(trends),
        summary: getData(summary)
      });
      setError(null);
    } catch (err) {
      console.error('Failed to load historical data:', err);
      setError('Failed to load historical comparisons. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleTrendsWeeksChange = (weeks) => {
    setTrendsWeeks(parseInt(weeks));
  };

  if (loading) {
    return (
      <div className="historical-comparison loading">
        <div className="loading-spinner" />
        <p>Loading historical data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="historical-comparison error">
        <AlertCircle size={48} style={{ marginBottom: '16px', color: '#dc3545' }} />
        <p>{error}</p>
        <button onClick={fetchHistoricalData}>Retry</button>
      </div>
    );
  }

  if (!historicalData) return null;

  const { waitTimes, sales, busyness, trends, summary } = historicalData;
  const orderSummary = summary.orders || {};
  const waitTimeSummary = summary.wait_times || {};
  const totalRecords = (orderSummary.total_records || 0) + (waitTimeSummary.total_records || 0);
  const summaryDateRange = orderSummary.date_range || waitTimeSummary.date_range || {};

  return (
    <div className="historical-comparison">
      <div className="comparison-header">
        <div className="header-main">
          <History size={28} className="header-icon" />
          <h2 className="section-title">Historical Analysis</h2>
        </div>
        <div className="view-controls">
          <button 
            className={`view-btn ${viewMode === 'overview' ? 'active' : ''}`}
            onClick={() => setViewMode('overview')}
          >
            Overview
          </button>
          <button 
            className={`view-btn ${viewMode === 'details' ? 'active' : ''}`}
            onClick={() => setViewMode('details')}
          >
            Details
          </button>
          <button 
            className={`view-btn ${viewMode === 'trends' ? 'active' : ''}`}
            onClick={() => setViewMode('trends')}
          >
            Trends
          </button>
        </div>
      </div>

      {/* Overview Mode */}
      {viewMode === 'overview' && (
        <div className="overview-grid">
          {/* Wait Times Card */}
          <div className="comparison-card wait-times">
            <div className="card-header">
              <Clock size={24} className="card-icon" />
              <h3>Wait Times</h3>
            </div>
            <div className="comparison-row">
              <div className="period today">
                <span className="period-label">Today</span>
                <span className="period-value">
                  {formatValue(waitTimes.today?.average_minutes, '0')} min
                </span>
                <span className="period-subvalue">
                  {formatValue(waitTimes.today?.count, '0')} orders
                </span>
              </div>
              <div className="period last-week">
                <span className="period-label">Last Week</span>
                <span className="period-value">
                  {formatValue(waitTimes.last_week?.average_minutes, '0')} min
                </span>
                <TrendIndicator value={waitTimes.last_week?.change_percent} />
              </div>
              <div className="period last-year">
                <span className="period-label">Last Year</span>
                <span className="period-value">
                  {formatValue(waitTimes.last_year?.average_minutes, '0')} min
                </span>
                <TrendIndicator value={waitTimes.last_year?.change_percent} />
              </div>
            </div>
            {waitTimes.insight && (
              <div className="insight-box">
                <span className="insight-icon">💡</span>
                <span className="insight-text">{waitTimes.insight}</span>
              </div>
            )}
          </div>

          {/* Sales Card */}
          <div className="comparison-card sales">
            <div className="card-header">
              <ShoppingCart size={24} className="card-icon" />
              <h3>Sales Performance</h3>
            </div>
            <div className="comparison-row">
              <div className="period today">
                <span className="period-label">Today</span>
                <span className="period-value">
                  ${formatValue(sales.today?.total?.toLocaleString(), '0')}
                </span>
                <span className="period-subvalue">
                  {formatValue(sales.today?.order_count, '0')} orders
                </span>
              </div>
              <div className="period last-week">
                <span className="period-label">Last Week</span>
                <span className="period-value">
                  ${formatValue(sales.last_week?.total?.toLocaleString(), '0')}
                </span>
                <TrendIndicator value={sales.last_week?.change_percent} />
              </div>
              <div className="period last-year">
                <span className="period-label">Last Year</span>
                <span className="period-value">
                  ${formatValue(sales.last_year?.total?.toLocaleString(), '0')}
                </span>
                <TrendIndicator value={sales.last_year?.change_percent} />
              </div>
            </div>
            {sales.insight && (
              <div className="insight-box">
                <span className="insight-icon">📊</span>
                <span className="insight-text">{sales.insight}</span>
              </div>
            )}
          </div>

          {/* Busyness Card */}
          <div className="comparison-card busyness">
            <div className="card-header">
              <Users size={24} className="card-icon" />
              <h3>Busyness Level</h3>
            </div>
            <div className="comparison-row">
              <div className="period today">
                <span className="period-label">Today</span>
                <span className="period-value">
                  {formatValue(busyness.today?.orders_per_hour, '0')}/hr
                </span>
                <span className="period-subvalue">
                  {formatValue(busyness.today?.total_orders, '0')} total
                </span>
              </div>
              <div className="period last-week">
                <span className="period-label">Last Week</span>
                <span className="period-value">
                  {formatValue(busyness.last_week?.orders_per_hour, '0')}/hr
                </span>
                <TrendIndicator value={busyness.last_week?.change_percent} />
              </div>
              <div className="period last-year">
                <span className="period-label">Last Year</span>
                <span className="period-value">
                  {formatValue(busyness.last_year?.orders_per_hour, '0')}/hr
                </span>
                <TrendIndicator value={busyness.last_year?.change_percent} />
              </div>
            </div>
            {busyness.insight && (
              <div className="insight-box">
                <span className="insight-icon">📈</span>
                <span className="insight-text">{busyness.insight}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Details Mode */}
      {viewMode === 'details' && (
        <div className="details-section">
          <h3>Detailed Metrics</h3>
          <div className="metrics-table">
            <p style={{ color: '#6c757d', padding: '20px' }}>
              Detailed table view coming soon...
            </p>
          </div>
          <div className="current-range-display">
            <Calendar size={16} />
            Data range: {dateRange?.startDate} to {dateRange?.endDate}
          </div>
        </div>
      )}

      {/* Trends Mode */}
      {viewMode === 'trends' && (
        <div className="trends-section">
          <div className="trends-header">
            <h3>{trendsWeeks}-Week Trends</h3>
            <select 
              value={trendsWeeks} 
              onChange={(e) => handleTrendsWeeksChange(e.target.value)}
              className="trends-weeks-select"
            >
              <option value="4">4 Weeks</option>
              <option value="8">8 Weeks</option>
              <option value="12">12 Weeks</option>
              <option value="16">16 Weeks</option>
            </select>
          </div>
          
          {trends.weekly_data && trends.weekly_data.length > 0 ? (
            <>
              <div className="trends-chart">
                <p style={{ color: '#6c757d', padding: '20px' }}>
                  Chart visualization would go here
                  {trends.weekly_data?.length} data points available
                </p>
              </div>
              <div className="trend-summary">
                <div className="trend-item">
                  <span className="trend-label">Peak Wait Time</span>
                  <span className="trend-value">{formatValue(trends.peak_wait_time)}</span>
                </div>
                <div className="trend-item">
                  <span className="trend-label">Avg Daily Sales</span>
                  <span className="trend-value">
                    ${formatValue(trends.avg_daily_sales?.toLocaleString(), '0')}
                  </span>
                </div>
                <div className="trend-item">
                  <span className="trend-label">Busiest Day</span>
                  <span className="trend-value">{formatValue(trends.busiest_day)}</span>
                </div>
              </div>
            </>
          ) : (
            <div className="insight-box" style={{ marginTop: '20px' }}>
              <span className="insight-icon">📊</span>
              <span className="insight-text">
                No trend data available for the last {trendsWeeks} weeks
              </span>
            </div>
          )}
          <div className="current-range-display">
            Trend period: {trends.start_date || 'N/A'} to {trends.end_date || 'N/A'}
          </div>
        </div>
      )}

      {/* Data Summary */}
      <div className="summary-footer">
        <div className="summary-item">
          <span className="summary-label">Data Range</span>
          <span className="summary-value">
            {dateRange?.startDate || 'N/A'} to {dateRange?.endDate || 'N/A'}
          </span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Total Records</span>
          <span className="summary-value">
            {totalRecords.toLocaleString()}
          </span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Active View</span>
          <span className="summary-value" style={{ textTransform: 'capitalize' }}>
            {viewMode}
          </span>
        </div>
      </div>

      {/* Debug Panel */}
      {process.env.NODE_ENV === 'development' && (
        <div className="debug-panel">
          <details className="debug-details">
            <summary>🔍 Historical Data Debug</summary>
            <div className="debug-content">
              <h4>Date Range:</h4>
              <pre>{JSON.stringify(dateRange, null, 2)}</pre>
              <h4>Wait Times:</h4>
              <pre>{JSON.stringify(waitTimes, null, 2)}</pre>
              <h4>Sales:</h4>
              <pre>{JSON.stringify(sales, null, 2)}</pre>
              <h4>Busyness:</h4>
              <pre>{JSON.stringify(busyness, null, 2)}</pre>
              <h4>Trends:</h4>
              <pre>{JSON.stringify(trends, null, 2)}</pre>
              <h4>Summary:</h4>
              <pre>{JSON.stringify(summary, null, 2)}</pre>
            </div>
          </details>
        </div>
      )}
    </div>
  );
};

const TrendIndicator = ({ value }) => {
  const formattedValue = formatPercent(value);
  
  if (formattedValue === null) {
    return <span className="trend-indicator">—</span>;
  }
  
  const isPositive = parseFloat(value) >= 0;
  return (
    <span className={`trend-indicator ${isPositive ? 'positive' : 'negative'}`}>
      {isPositive ? '↑' : '↓'} {formattedValue}%
    </span>
  );
};

export default HistoricalComparison;