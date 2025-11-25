import React, { useState } from 'react';
import Header from './Header.jsx';
import ChartSection from './Chartsection.jsx';
import HighlightCards from './Highlightcards.jsx';
import MetricsGrid from './Metricsgrid.jsx';
import InfoSections from './Infosections.jsx';
import './CSS/Dashboard.css';

const Dashboard = () => {
  const [selectedWeek, setSelectedWeek] = useState('this-week');

  const handleWeekChange = (week) => {
    setSelectedWeek(week);
    // Here you would typically fetch new data based on the selected week
    console.log('Week changed to:', week);
  };

  return (
    <div className="dashboard-container">
      <div className="container">
        <Header 
          selectedWeek={selectedWeek} 
          onWeekChange={handleWeekChange} 
        />
        
        <main className="dashboard-main">
          <HighlightCards />
          
          <ChartSection />
          
          <MetricsGrid />
          
          <InfoSections />
        </main>
        
        <footer className="dashboard-footer">
          <p>Restaurant Dashboard © 2024 | Last updated: {new Date().toLocaleTimeString()}</p>
        </footer>
      </div>
    </div>
  );
};

export default Dashboard;