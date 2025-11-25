import React from 'react';
import { Calendar, ChevronDown } from 'lucide-react';
import './CSS/Header.css';

const Header = ({ selectedWeek, onWeekChange }) => {
  return (
    <header className="dashboard-header">
      <div className="header-content">
        <div className="header-left">
          <h1 className="dashboard-title">Dashboard</h1>
          <span className="subtitle">Restaurant Analytics & Insights</span>
        </div>
        
        <div className="header-right">
          <div className="week-selector">
            <Calendar size={20} className="selector-icon" />
            <select 
              value={selectedWeek} 
              onChange={(e) => onWeekChange(e.target.value)}
              className="week-dropdown"
            >
              <option value="this-week">This Week</option>
              <option value="last-week">Last Week</option>
              <option value="last-month">Last Month</option>
              <option value="custom">Custom Range</option>
            </select>
            <ChevronDown size={16} className="dropdown-arrow" />
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;