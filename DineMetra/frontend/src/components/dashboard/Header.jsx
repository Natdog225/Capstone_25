import React, { useState } from 'react';
import { Calendar, LogOut, RefreshCw } from 'lucide-react';
import './CSS/Header.css';

const Header = ({ dateRange, onDateRangeChange, onLogout }) => {
  const today = new Date().toISOString().split('T')[0];
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleDateChange = (field, value) => {
    onDateRangeChange({ ...dateRange, [field]: value });
  };

  const handleQuickSelect = (days) => {
    const endDate = new Date();
    const startDate = new Date();
    
    if (days === 'month') {
      startDate.setMonth(startDate.getMonth() - 1);
    } else if (days === 'week') {
      startDate.setDate(startDate.getDate() - 7);
    } else if (days === 'today') {
      // Keep both as today
    } else {
      startDate.setDate(startDate.getDate() - days);
    }
    
    onDateRangeChange({
      startDate: startDate.toISOString().split('T')[0],
      endDate: endDate.toISOString().split('T')[0]
    });
  };

  const handleRefresh = () => {
    setIsRefreshing(true);
    // Trigger a re-render by setting the same dates
    onDateRangeChange({ ...dateRange });
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  // Calculate days between dates for display
  const calculateDaysBetween = () => {
    const start = new Date(dateRange.startDate);
    const end = new Date(dateRange.endDate);
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays + 1; // +1 to include both start and end dates
  };

  return (
    <header className="dashboard-header">
      <div className="header-content">
        <div className="header-left">
  <div className="logo-container">
    <img src="./CSS/DineMetra_Logo.png" alt="DineMetra Logo" />
  </div>
  <div className="title-section">
    <h1 className="dashboard-title">Dashboard</h1>
    <p className="subtitle">Plan Smarter. Serve Better.</p>
  </div>
</div>
        
        <div className="header-right">
          {/* Date Range Selector */}
          <div className="date-range-container">
            <div className="date-range-inputs">
              <div className="date-input-group">
                <label htmlFor="start-date" className="date-label">From</label>
                <div className="date-input-wrapper">
                  <Calendar size={16} className="date-icon" />
                  <input 
                    id="start-date"
                    type="date" 
                    value={dateRange.startDate}
                    onChange={(e) => handleDateChange('startDate', e.target.value)}
                    max={dateRange.endDate}
                    className="date-input"
                  />
                </div>
              </div>
              
              <span className="date-separator">→</span>
              
              <div className="date-input-group">
                <label htmlFor="end-date" className="date-label">To</label>
                <div className="date-input-wrapper">
                  <Calendar size={16} className="date-icon" />
                  <input 
                    id="end-date"
                    type="date" 
                    value={dateRange.endDate}
                    onChange={(e) => handleDateChange('endDate', e.target.value)}
                    min={dateRange.startDate}
                    max={today}
                    className="date-input"
                  />
                </div>
              </div>
              
              <button 
                onClick={handleRefresh}
                className="refresh-date-btn"
                disabled={isRefreshing}
                title="Refresh data"
              >
                <RefreshCw size={18} className={isRefreshing ? 'spinning' : ''} />
              </button>
            </div>
            
            {/* Quick Select Buttons */}
            <div className="quick-select-buttons">
              <button 
                onClick={() => handleQuickSelect('today')}
                className="quick-select-btn"
              >
                Today
              </button>
              <button 
                onClick={() => handleQuickSelect('week')}
                className="quick-select-btn"
              >
                Last 7 Days
              </button>
              <button 
                onClick={() => handleQuickSelect(30)}
                className="quick-select-btn"
              >
                Last 30 Days
              </button>
              <button 
                onClick={() => handleQuickSelect('month')}
                className="quick-select-btn"
              >
                Last Month
              </button>
            </div>
            
            {/* Display selected range info */}
            <div className="date-range-info">
              <span className="range-days">{calculateDaysBetween()} days selected</span>
            </div>
          </div>
          
          <button 
            onClick={onLogout}
            className="logout-button"
          >
            <LogOut size={18} />
            <span>Logout</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;