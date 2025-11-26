import React, { useState } from 'react';
import Header from './Header.jsx';
import ChartSection from './Chartsection.jsx';
import HighlightCards from './Highlightcards.jsx';
import MetricsGrid from './Metricsgrid.jsx';
import InfoSections from './Infosections.jsx';
import './CSS/Dashboard.css';
import { signOut } from 'firebase/auth';
import { auth } from '../../firebase';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const navigate = useNavigate();
  const [selectedWeek, setSelectedWeek] = useState('this-week');

  const handleWeekChange = (week) => {
    setSelectedWeek(week);
    console.log('Week changed to:', week);
  };

  const handleLogout = async () => {
    try {
      await signOut(auth);
      navigate('/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <div className="dashboard-container">
      <div className="container">
        <Header 
          selectedWeek={selectedWeek} 
          onWeekChange={handleWeekChange}
          onLogout={handleLogout}
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