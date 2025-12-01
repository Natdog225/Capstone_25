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
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [apiStatus, setApiStatus] = useState('connecting');

  // Load ALL dashboard data in ONE call
  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const [completeData, userProfile] = await Promise.all([
          dinemetraAPI.getCompleteDashboard(),
          dinemetraAPI.getUserProfile()
        ]);
        
        setDashboardData({
          highlights: completeData.highlights,
          chartData: completeData.chartData,
          metrics: completeData.metrics,
          infoData: completeData.infoData,
          userProfile: userProfile
        });
        setApiStatus('connected');
      } catch (error) {
        console.error('Failed to load dashboard:', error);
        setApiStatus('failed');
        // Use mock data or show error
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
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

  if (loading) {
    return <div className="loading-screen">Loading your restaurant insights...</div>;
  }

  if (!dashboardData) {
    return <div className="error-screen">Failed to load dashboard data</div>;
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
          <MetricsGrid metrics={dashboardData.metrics} />
          <PredictionsPanel />
          <InfoSections infoData={dashboardData.infoData} />
        </main>
        
        <footer className="dashboard-footer">
          <p>Restaurant Dashboard © 2024 | Last updated: {new Date().toLocaleTimeString()}</p>
        </footer>
      </div>
    </div>
  );
};

export default Dashboard;
