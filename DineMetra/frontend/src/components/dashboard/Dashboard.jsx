import React, { useState, useEffect } from 'react';
import { ShoppingCart, Wine, Beer, Users, TrendingUp } from 'lucide-react';import Header from './Header';
import ChartSection from './Chartsection';
import HighlightCards from './Highlightcards';
import MetricsGrid from './Metricsgrid';
import InfoSections from './Infosections';
import PredictionsPanel from '../PredictionsPanel';
import { auth } from '../../firebase';
import { signOut } from 'firebase/auth';
import { dinemetraAPI } from '../../services/dinemetraService';
import { useNavigate } from 'react-router-dom';
import './CSS/Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [selectedWeek, setSelectedWeek] = useState('this-week');
  const [periodRange, setPeriodRange] = useState('30-days');
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [apiStatus, setApiStatus] = useState('connecting');

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        setLoading(true);
        
        // Fetch all dashboard data in parallel
        const [completeData, userProfile] = await Promise.all([
          dinemetraAPI.getCompleteDashboard(),
          dinemetraAPI.getUserProfile()
        ]);
        
        setDashboardData({
          highlights: completeData.highlights || [],
          chartData: completeData.chartData || [],
          metrics: completeData.metrics || {},
          infoData: completeData.infoData || {},
          userProfile: userProfile
        });
        
        setApiStatus('connected');
      } catch (error) {
        console.error('Failed to load dashboard:', error);
        setApiStatus('failed');
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, []);

  const handleWeekChange = (week) => {
    setSelectedWeek(week);
  };

  const handlePeriodChange = (period) => {
    setPeriodRange(period);
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

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-screen">
          <h1>Loading Dashboard...</h1>
          <p>Fetching your restaurant insights</p>
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  if (apiStatus === 'failed' || !dashboardData) {
    return (
      <div className="dashboard-container">
        <div className="error-screen">
          <h2>⚠️ Unable to Load Dashboard</h2>
          <p>The API is currently unavailable. Please check your connection or try again later.</p>
          <button onClick={() => window.location.reload()} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="container">
        <Header 
          selectedWeek={selectedWeek} 
          onWeekChange={handleWeekChange}
          onLogout={handleLogout}
          userProfile={dashboardData.userProfile}
        />
        
        <main className="dashboard-main">
          <HighlightCards highlights={dashboardData.highlights} />
          <ChartSection weekRange={selectedWeek} />
          <MetricsGrid 
            periodRange={periodRange} 
            onPeriodChange={handlePeriodChange}
          />
          <PredictionsPanel />
          <InfoSections infoData={dashboardData.infoData} />
        </main>
        
        <footer className="dashboard-footer">
          <p>Restaurant Dashboard © 2024 | Last updated: {new Date().toLocaleTimeString()}</p>
        </footer>
        
        {/* Optional: API status indicator */}
        <div className={`api-status ${apiStatus}`}>
          {apiStatus === 'connected' ? '✅ API Connected' : '❌ API Offline'}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
