import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { TrendingUp } from 'lucide-react';
import { dinemetraAPI } from '../../services/dinemetraService.js';
import './CSS/Chartsection.css';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip">
        <p className="tooltip-label">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} style={{ color: entry.color }}>
            {entry.name}: ${entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const ChartSection = ({ weekRange = 'this-week' }) => {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchChartData = async () => {
      try {
        setLoading(true);
        const data = await dinemetraAPI.getSalesChart(weekRange);
        setChartData(data);
        setError(null);
      } catch (err) {
        console.error('Failed to load chart data:', err);
        setError('Failed to load chart data');
        setChartData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchChartData();
  }, [weekRange]);

  // Calculate dynamic stats from real data
  const calculateStats = () => {
    // Check if it's actually an array
    if (!Array.isArray(chartData) || chartData.length === 0) {
      return { variance: 0 };
    }
    
    try {
      const thisWeekTotal = chartData.reduce((sum, d) => sum + (d.thisWeek || 0), 0);
      const pastWeekTotal = chartData.reduce((sum, d) => sum + (d.pastData || 0), 0);
      const variance = pastWeekTotal > 0 ? ((thisWeekTotal - pastWeekTotal) / pastWeekTotal * 100) : 0;
      
      return { variance };
    } catch (error) {
      console.error('Error calculating stats:', error);
      return { variance: 0 };
    }
  };

  const { variance } = calculateStats();

  if (loading) {
    return (
      <div className="chart-section card loading">
        <div className="loading-spinner">Loading chart data...</div>
      </div>
    );
  }

  if (error || !chartData) {
    return (
      <div className="chart-section card error">
        <p className="error-message">⚠️ {error || 'No chart data available'}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  return (
    <div className="chart-section card">
      <div className="chart-header">
        <h2 className="section-title">Sales Overview</h2>
        <div className="chart-stats">
          <div className="stat-item">
            <TrendingUp size={18} className={`stat-icon ${variance >= 0 ? 'up' : 'down'}`} />
            <span className={`stat-value ${variance >= 0 ? 'up' : 'down'}`}>
              {variance >= 0 ? '+' : ''}{variance.toFixed(1)}%
            </span>
            <span className="stat-label">vs last week</span>
          </div>
        </div>
      </div>

      <div className="chart-legend-custom">
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#ffb917' }}></span>
          <span>This Week</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#206EB6' }}></span>
          <span>Past Data</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#4CAF50' }}></span>
          <span>AI Predicted</span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
          <XAxis 
            dataKey="day" 
            tick={{ fill: '#ffffff' }}
            axisLine={{ stroke: 'rgba(255, 255, 255, 0.2)' }}
          />
          <YAxis 
            tick={{ fill: '#ffffff' }}
            axisLine={{ stroke: 'rgba(255, 255, 255, 0.2)' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar 
            dataKey="thisWeek" 
            fill="#ffb917" 
            radius={[6, 6, 0, 0]}
            name="This Week"
          />
          <Bar 
            dataKey="pastData" 
            fill="#206EB6" 
            radius={[6, 6, 0, 0]}
            name="Past Data"
          />
          <Bar 
            dataKey="actual" 
            fill="#4CAF50" 
            radius={[6, 6, 0, 0]}
            name="AI Predicted"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ChartSection;