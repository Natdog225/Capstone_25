import React, { useState, useEffect } from 'react';
import { ShoppingCart, Wine, Beer, Users, TrendingUp } from 'lucide-react';import Header from './Header';
import ChartSection from './Chartsection';
import HighlightCards from './Highlightcards';
import MetricsGrid from './Metricsgrid';
import InfoSections from './Infosections';
import PredictionsPanel from '../PredictionsPanel'; // Add this
import { auth } from '../../firebase';
import { signOut } from 'firebase/auth';
import { dinemetraAPI } from '../../services/dinemetraService'; // Add this
import { useNavigate } from 'react-router-dom';
import './CSS/Dashboard.css';

// Keep your existing mock data
const MOCK_DATA = {
  highlights: [
    { id: 1, title: 'Big Event', icon: 'Calendar', color: 'blue', details: 'Jazz Night - Saturday', subDetails: 'Expected: 150+ guests', importance: 'high' },
    { id: 2, title: 'Weather Alert', icon: 'CloudRain', color: 'orange', details: 'Rain 90% Saturday', subDetails: 'Prepare indoor seating', importance: 'high' },
    { id: 3, title: 'Active Promo', icon: 'Tag', color: 'green', details: 'Happy Hour Extended', subDetails: '45% off selected drinks', importance: 'medium' }
  ],
  chartData: [
    { day: 'Mon', thisWeek: 145, pastData: 120, actual: 138 },
    { day: 'Tue', thisWeek: 168, pastData: 145, actual: 160 },
    { day: 'Wed', thisWeek: 135, pastData: 130, actual: 142 },
    { day: 'Thu', thisWeek: 178, pastData: 165, actual: 170 },
    { day: 'Fri', thisWeek: 220, pastData: 195, actual: 210 },
    { day: 'Sat', thisWeek: 265, pastData: 240, actual: 255 },
    { day: 'Sun', thisWeek: 245, pastData: 225, actual: 238 }
  ],
  metrics: {
    categories: [
      { id: 1, title: 'Best Sellers', icon: ShoppingCart, items: [{ name: 'Burger Special', value: '156', trend: 'up' }, { name: 'Fish Tacos', value: '132', trend: 'up' }, { name: 'Caesar Salad', value: '98', trend: 'down' }] },
      { id: 2, title: 'Bar Drinks', icon: Wine, items: [{ name: 'Cocktails', value: '245', trend: 'up' }, { name: 'Wine', value: '189', trend: 'stable' }, { name: 'Spirits', value: '156', trend: 'up' }] },
      { id: 3, title: 'Top Beers', icon: Beer, items: [{ name: 'IPA Draft', value: '98', trend: 'up' }, { name: 'Lager', value: '76', trend: 'stable' }, { name: 'Stout', value: '54', trend: 'down' }] }
    ],
    summaries: [
      { id: 4, title: 'Labor Cost', icon: Users, percentage: '28.5%', target: '30%', status: 'good', details: 'Within target range' },
      { id: 5, title: 'Actual vs Expected', icon: TrendingUp, percentage: '104%', variance: '+$4,200', status: 'excellent', details: 'Exceeding projections' }
    ]
  }
};

const Dashboard = () => {
  const navigate = useNavigate();
  const [selectedWeek, setSelectedWeek] = useState('this-week');
  const [apiStatus, setApiStatus] = useState('checking');

  // Check API health on mount
  useEffect(() => {
    dinemetraAPI.healthCheck().then(status => {
      setApiStatus(status ? 'connected' : 'failed');
    });
  }, []);

  const handleWeekChange = (week) => {
    setSelectedWeek(week);
  };

  const handleLogout = async () => {
    try {
      await signOut(auth);
      localStorage.removeItem('firebaseToken');
      navigate('/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const statusIndicator = (
    <div style={{
      position: 'fixed',
      bottom: '10px',
      right: '10px',
      padding: '6px 12px',
      borderRadius: '20px',
      fontSize: '12px',
      background: apiStatus === 'connected' ? '#4CAF50' : '#666',
      color: 'white',
      zIndex: 1000
    }}>
      {apiStatus === 'connected' ? 'AI API Connected' : 'AI API Offline'}
    </div>
  );

  return (
    <div className="dashboard-container">
      <div className="container">
        <Header 
          selectedWeek={selectedWeek} 
          onWeekChange={handleWeekChange}
          onLogout={handleLogout}
        />
        
        <main className="dashboard-main">
          <HighlightCards highlights={MOCK_DATA.highlights} />
          
          <ChartSection chartData={MOCK_DATA.chartData} />
          
          <MetricsGrid metrics={MOCK_DATA.metrics} />
          
          <PredictionsPanel /> {/* Add this - the ONLY real API integration */}
          
          <InfoSections infoData={MOCK_DATA.infoData} />
        </main>
        
        <footer className="dashboard-footer">
          <p>Restaurant Dashboard © 2024 | Last updated: {new Date().toLocaleTimeString()}</p>
        </footer>
        
        {statusIndicator}
      </div>
    </div>
  );
};

export default Dashboard;