import React from 'react';
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
import './CSS/Chartsection.css';

const ChartSection = ({ chartData = [] }) => {
  const defaultData = chartData.length > 0 ? chartData : [
    { day: 'Mon', thisWeek: 145, pastData: 120, actual: 138 },
    { day: 'Tue', thisWeek: 168, pastData: 145, actual: 160 },
    { day: 'Wed', thisWeek: 135, pastData: 130, actual: 142 },
    { day: 'Thu', thisWeek: 178, pastData: 165, actual: 170 },
    { day: 'Fri', thisWeek: 220, pastData: 195, actual: 210 },
    { day: 'Sat', thisWeek: 265, pastData: 240, actual: 255 },
    { day: 'Sun', thisWeek: 245, pastData: 225, actual: 238 }
  ];

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

  return (
    <div className="chart-section card">
      <div className="chart-header">
        <h2 className="section-title">Sales Overview</h2>
        <div className="chart-stats">
          <div className="stat-item">
            <TrendingUp size={18} className="stat-icon up" />
            <span className="stat-value up">+12%</span>
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
          <span>Actual</span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={defaultData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis 
            dataKey="day" 
            tick={{ fill: '#666' }}
            axisLine={{ stroke: '#e0e0e0' }}
          />
          <YAxis 
            tick={{ fill: '#666' }}
            axisLine={{ stroke: '#e0e0e0' }}
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
            name="Actual"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ChartSection;