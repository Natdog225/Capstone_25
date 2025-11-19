// App.js - Main Router
import React, { useState } from 'react';
import VisionUILanding from './components/LandingPage';
import Dashboard from './components/Dashboard';

function App() {
  const [currentPage, setCurrentPage] = useState('landing');

  return (
    <div style={{ minHeight: '100vh' }}>
      {currentPage === 'landing' ? (
        <VisionUILanding onGetStarted={() => setCurrentPage('dashboard')} />
      ) : (
        <Dashboard onBack={() => setCurrentPage('landing')} />
      )}
    </div>
  );
}

export default App;