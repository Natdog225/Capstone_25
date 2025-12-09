import React, { useState, useEffect } from 'react';
import { History, Clock, ShoppingCart, Users, AlertCircle, Calendar, RefreshCw, TrendingUp, DollarSign, Activity } from 'lucide-react';
import { dinemetraAPI } from '../../services/dinemetraService.js';
import './CSS/HistoricalComparison.css';

// Utility functions
const formatValue = (value, fallback = 'N/A') => (value === null || value === undefined || value === '') ? fallback : value;
const formatPercent = (value) => (value === null || value === undefined) ? null : parseFloat(value).toFixed(1);
const formatCurrency = (value) => `$${Math.round(value || 0).toLocaleString()}`;

const HistoricalComparison = ({ dateRange, onDateRangeChange }) => {
  const [historicalData, setHistoricalData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('overview');
  const [trendsWeeks, setTrendsWeeks] = useState(8);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const today = new Date().toISOString().split('T')[0];
  const selectedDate = dateRange?.startDate;

  useEffect(() => {
    if (selectedDate) {
      fetchHistoricalData();
    }
  }, [selectedDate, viewMode, trendsWeeks]);

  const fetchHistoricalData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch all data in parallel
      const [waitTimes, sales, busyness, trends, summary] = await Promise.all([
        dinemetraAPI.compareWaitTimes(selectedDate),
        dinemetraAPI.compareSales(selectedDate),
        dinemetraAPI.compareBusyness(selectedDate),
        viewMode === 'trends' 
          ? dinemetraAPI.getDailyTrends(trendsWeeks * 7, selectedDate)
          : dinemetraAPI.getDailyTrends(30, selectedDate),
        dinemetraAPI.getHistoricalSummary()
      ]);

      setHistoricalData({
        waitTimes,
        sales,
        busyness,
        trends,
        summary
      });
    } catch (err) {
      console.error('Failed to load historical data:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to load data');
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  const handleDateChange = (e) => {
    const value = e.target.value;
    onDateRangeChange({ startDate: value, endDate: value });
  };

  const handleRefresh = () => {
    setIsRefreshing(true);
    fetchHistoricalData();
  };

  const handleTrendsWeeksChange = (e) => {
    setTrendsWeeks(parseInt(e.target.value));
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
        <AlertCircle size={48} className="header-icon" />
        <p>{error}</p>
        <button onClick={fetchHistoricalData} className="retry-btn">
          Retry
        </button>
      </div>
    );
  }

  const { waitTimes = {}, sales = {}, busyness = {}, trends = {}, summary = {} } = historicalData;
  const orderSummary = summary.orders || {};
  const waitTimeSummary = summary.wait_times || {};
  const totalRecords = (orderSummary.total_records || 0) + (waitTimeSummary.total_records || 0);

  return (
    <div className="historical-comparison">
      {/* Date Selector */}
      <DateSelector 
        selectedDate={selectedDate}
        onDateChange={handleDateChange}
        onRefresh={handleRefresh}
        isRefreshing={isRefreshing}
        today={today}
      />

      {/* Header */}
      <Header 
        viewMode={viewMode}
        onViewModeChange={setViewMode}
      />

      {/* Content */}
      <div className="content-area">
        {viewMode === 'overview' && (
          <OverviewView 
            waitTimes={waitTimes}
            sales={sales}
            busyness={busyness}
          />
        )}

        {viewMode === 'details' && (
          <DetailsView 
            waitTimes={waitTimes}
            sales={sales}
            busyness={busyness}
            selectedDate={selectedDate}
          />
        )}

        {viewMode === 'trends' && (
          <TrendsView 
            trends={trends}
            trendsWeeks={trendsWeeks}
            onWeeksChange={handleTrendsWeeksChange}
          />
        )}
      </div>

      {/* Summary Footer */}
      <SummaryFooter
        selectedDate={selectedDate}
        totalRecords={totalRecords}
        viewMode={viewMode}
      />
    </div>
  );
};

// SUB-COMPONENTS

const DateSelector = ({ selectedDate, onDateChange, onRefresh, isRefreshing, today }) => (
  <div className="date-range-container">
    <div className="date-range-inputs">
      <div className="date-input-group">
        <label htmlFor="single-date" className="date-label">Select Date</label>
        <div className="date-input-wrapper">
          <Calendar size={16} className="date-icon" />
          <input 
            id="single-date"
            type="date" 
            value={selectedDate || ''}
            onChange={onDateChange}
            max={today}
            className="date-input"
          />
          <button 
            onClick={onRefresh}
            className="refresh-date-btn"
            disabled={isRefreshing}
            title="Refresh data"
          >
            <RefreshCw size={18} className={isRefreshing ? 'spinning' : ''} />
          </button>
        </div>
      </div>
    </div>
  </div>
);

const Header = ({ viewMode, onViewModeChange }) => (
  <div className="comparison-header">
    <div className="header-main">
      <History size={28} className="header-icon" />
      <h2 className="section-title">Historical Analysis</h2>
    </div>
    <div className="view-controls">
      <button className={`view-btn ${viewMode === 'overview' ? 'active' : ''}`} onClick={() => onViewModeChange('overview')}>
        Overview
      </button>
      <button className={`view-btn ${viewMode === 'details' ? 'active' : ''}`} onClick={() => onViewModeChange('details')}>
        Details
      </button>
      <button className={`view-btn ${viewMode === 'trends' ? 'active' : ''}`} onClick={() => onViewModeChange('trends')}>
        Trends
      </button>
    </div>
  </div>
);

const OverviewView = ({ waitTimes, sales, busyness }) => (
  <div className="overview-grid">
    <MetricCard
      icon={<Clock className="card-icon" />}
      title="Wait Times"
      metric={waitTimes}
      dataKey="average_minutes"
      unit="min"
      countKey="count"
    />
    <MetricCard
      icon={<DollarSign className="card-icon" />}
      title="Sales Performance"
      metric={sales}
      dataKey="total"
      format={(v) => formatCurrency(v)}
      countKey="order_count"
    />
    <MetricCard
      icon={<Activity className="card-icon" />}
      title="Busyness Level"
      metric={busyness}
      dataKey="orders_per_hour"
      unit="/hr"
      countKey="total_orders"
    />
  </div>
);

const MetricCard = ({ icon, title, metric, dataKey, unit = '', format = null, countKey }) => {
  const todayVal = metric.today?.[dataKey];
  const weekVal = metric.last_week?.[dataKey];
  const yearVal = metric.last_year?.[dataKey];

  return (
    <div className="comparison-card">
      <div className="card-header">
        {icon}
        <h3>{title}</h3>
      </div>
      <div className="comparison-row">
        <Period label="Selected Date" value={format ? format(todayVal) : `${formatValue(todayVal)}${unit}`} subValue={`${formatValue(metric.today?.[countKey])} orders`} />
        <Period label="7 Days Prior" value={format ? format(weekVal) : `${formatValue(weekVal)}${unit}`} trend={metric.last_week?.change_percent} />
        <Period label="1 Year Prior" value={format ? format(yearVal) : `${formatValue(yearVal)}${unit}`} trend={metric.last_year?.change_percent} />
      </div>
      {metric.insight && (
        <div className="insight-box">
          <span className="insight-icon">💡</span>
          <span className="insight-text">{metric.insight}</span>
        </div>
      )}
    </div>
  );
};

const Period = ({ label, value, subValue, trend }) => (
  <div className="period today">
    <span className="period-label">{label}</span>
    <span className="period-value">{value}</span>
    {subValue && <span className="period-subvalue">{subValue}</span>}
    {trend !== undefined && <TrendIndicator value={trend} />}
  </div>
);

const DetailsView = ({ waitTimes, sales, busyness, selectedDate }) => (
  <div className="details-section">
    <h3>Detailed Metrics Comparison</h3>
    <DetailsTable waitTimes={waitTimes} sales={sales} busyness={busyness} />
    <div className="current-range-display">
      <Calendar size={16} />
      Selected date: {selectedDate}
    </div>
  </div>
);

const DetailsTable = ({ waitTimes, sales, busyness }) => {
  const rows = [
    { metric: 'Avg Wait Time', unit: 'min', keys: ['average_minutes'], sources: [waitTimes] },
    { metric: 'Wait Time Orders', unit: '', keys: ['count'], sources: [waitTimes] },
    { metric: 'Total Sales', unit: '', keys: ['total'], sources: [sales], format: (v) => formatCurrency(v) },
    { metric: 'Sales Orders', unit: '', keys: ['order_count'], sources: [sales] },
    { metric: 'Orders/Hour', unit: '/hr', keys: ['orders_per_hour'], sources: [busyness] },
    { metric: 'Total Orders', unit: '', keys: ['total_orders'], sources: [busyness] }
  ];

  return (
    <table className="details-table">
      <thead>
        <tr>
          <th>Metric</th>
          <th>Selected Date</th>
          <th>7 Days Prior</th>
          <th>1 Year Prior</th>
          <th>Week Change</th>
          <th>Year Change</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row, idx) => {
          const todayVal = row.sources[0]?.today?.[row.keys[0]];
          const weekVal = row.sources[0]?.last_week?.[row.keys[0]];
          const yearVal = row.sources[0]?.last_year?.[row.keys[0]];
          const weekChange = row.sources[0]?.last_week?.change_percent;
          const yearChange = row.sources[0]?.last_year?.change_percent;

          const display = (val) => {
            if (val === null || val === undefined) return 'N/A';
            return row.format ? row.format(val) : `${val}${row.unit}`;
          };

          return (
            <tr key={idx}>
              <td><strong>{row.metric}</strong></td>
              <td>{display(todayVal)}</td>
              <td>{display(weekVal)}</td>
              <td>{display(yearVal)}</td>
              <td><TrendIndicator value={weekChange} /></td>
              <td><TrendIndicator value={yearChange} /></td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};

const TrendsView = ({ trends, trendsWeeks, onWeeksChange }) => {
  const hasData = trends?.daily_data && trends.daily_data.length > 0;
  const stats = trends.summary_stats || {};

  return (
    <div className="trends-section">
      <div className="trends-header">
        <h3>{trendsWeeks}-Week Trend Analysis</h3>
        <select value={trendsWeeks} onChange={onWeeksChange} className="trends-weeks-select">
          <option value="4">4 Weeks</option>
          <option value="8">8 Weeks</option>
          <option value="12">12 Weeks</option>
          <option value="16">16 Weeks</option>
        </select>
      </div>
      
      {hasData ? (
        <>
          <div className="trends-chart">
            <div className="chart-placeholder">
              <div className="chart-header">
                <TrendingUp size={32} className="chart-icon" />
                <h4>Daily Performance Trends</h4>
              </div>
              <p className="chart-info">
                📈 {trends.daily_data.length} data points available
              </p>
              <p className="chart-range">
                {trends.period?.start_date} to {trends.period?.end_date}
              </p>
            </div>
          </div>
          
          <div className="trend-summary">
            <TrendStat label="Peak Wait Time" value={`${formatValue(stats.peak_wait_time)} min`} />
            <TrendStat label="Avg Wait Time" value={`${formatValue(stats.avg_wait_time)} min`} />
            <TrendStat label="Avg Daily Sales" value={formatCurrency(stats.avg_daily_sales)} />
            <TrendStat label="Total Sales" value={formatCurrency(stats.total_sales)} />
            <TrendStat label="Total Orders" value={stats.total_orders?.toLocaleString()} />
            <TrendStat label="Busiest Day" value={stats.busiest_day_of_week} />
            <TrendStat label="Days Analyzed" value={stats.days_analyzed} />
            <TrendStat 
              label="Trend Direction" 
              value={stats.trend_direction || 'stable'}
              className={stats.trend_direction}
            />
          </div>
        </>
      ) : (
        <div className="insight-box">
          <span className="insight-icon">📊</span>
          <span className="insight-text">
            No trend data available for the last {trendsWeeks} weeks
          </span>
        </div>
      )}
    </div>
  );
};

const TrendStat = ({ label, value, className = '' }) => (
  <div className={`trend-item ${className}`}>
    <span className="trend-label">{label}</span>
    <span className="trend-value">{value}</span>
  </div>
);

const SummaryFooter = ({ selectedDate, totalRecords, viewMode }) => (
  <div className="summary-footer">
    <div className="summary-item">
      <span className="summary-label">Selected Date</span>
      <span className="summary-value">{selectedDate || 'N/A'}</span>
    </div>
    <div className="summary-item">
      <span className="summary-label">Total Records</span>
      <span className="summary-value">{totalRecords.toLocaleString()}</span>
    </div>
    <div className="summary-item">
      <span className="summary-label">Active View</span>
      <span className="summary-value" style={{ textTransform: 'capitalize' }}>{viewMode}</span>
    </div>
  </div>
);


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