import React, { useState, useEffect } from 'react';
import Header from './Header';
import ChartSection from './Chartsection';
import HighlightCards from './Highlightcards';
import MetricsGrid from './Metricsgrid';
import InfoSections from './Infosections';
import PredictionsPanel from '../PredictionsPanel';
import ApiStatus from './ApiStatus'; // Add this import
import { auth } from '../../firebase';
import { signOut } from 'firebase/auth';
import { dinemetraAPI } from '../../services/dinemetraService';
import { useNavigate } from 'react-router-dom';
import { XCircle } from 'lucide-react';
import './CSS/Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  
  // Unified date range state
  const today = new Date().toISOString().split('T')[0];
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
  
  const [dateRange, setDateRange] = useState({
    startDate: thirtyDaysAgo,
    endDate: today
  });

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

  const handleDateRangeChange = (newRange) => {
    setDateRange(newRange);
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
        <div className="api-status-widget error">
          <XCircle size={24} className="status-icon error" />
          <div>
            <h3>API Connection Failed</h3>
            <p>Unable to connect to the server. Please check your connection.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="container">
        <Header 
          dateRange={dateRange}
          onDateRangeChange={handleDateRangeChange}
          onLogout={handleLogout}
        />
        
        <main className="dashboard-main">
          <HighlightCards dateRange={dateRange} highlights={dashboardData.highlights} />
          <ChartSection dateRange={dateRange} />
          <MetricsGrid dateRange={dateRange} />
          <PredictionsPanel />
          <InfoSections dateRange={dateRange} />
        </main>
        
        <footer className="dashboard-footer">
          <p>Restaurant Dashboard © 2025 | Last updated: {new Date().toLocaleTimeString()}</p>
        </footer>
        
        <ApiStatus />
      </div>
    </div>
  );
};

export default Dashboard;