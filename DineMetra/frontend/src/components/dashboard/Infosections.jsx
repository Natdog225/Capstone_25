import React from 'react';
import HistoricalComparison from './HistoricalComparison.jsx';
import './CSS/Infosections.css';

const InfoSections = ({ dateRange, onDateRangeChange }) => {
  return (
    <div className="info-sections">
      {/* Historical Comparison Component with dateRange and handler */}
      <HistoricalComparison 
        dateRange={dateRange} 
        onDateRangeChange={onDateRangeChange}
      />
    </div>
  );
};

export default InfoSections;