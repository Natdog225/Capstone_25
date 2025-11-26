import React from 'react';
import { Calendar, ChevronDown, LogOut } from 'lucide-react';
import './CSS/Header.css';

const Header = ({ selectedWeek, onWeekChange, onLogout }) => {
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
          
          <button 
            onClick={onLogout}
            className="logout-button"
            style={{
              marginLeft: '1rem',
              padding: '0.5rem 1rem',
              background: '#ff4444',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600',
              transition: 'background 0.3s',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
            onMouseEnter={(e) => e.target.style.background = '#cc0000'}
            onMouseLeave={(e) => e.target.style.background = '#ff4444'}
          >
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;