import React, { useState, useEffect } from 'react';
import { Calendar, Cloud, History, Users, ArrowRight } from 'lucide-react';
import { dinemetraAPI } from '../../services/dinemetraService.js';
import './CSS/Infosections.css';


const InfoSections = () => {
  const [infoData, setInfoData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchInfoSections = async () => {
      try {
        setLoading(true);
        const data = await dinemetraAPI.getInfoSections();
        setInfoData(data);
        setError(null);
      } catch (err) {
        console.error('Failed to load info sections:', err);
        setError('Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    fetchInfoSections();
  }, []);


  if (loading) {
    return (
      <div className="info-sections">
        <div className="info-grid">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="info-card card loading">
              <div className="loading-spinner">Loading...</div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error || !infoData) {
    return (
      <div className="info-sections">
        <div className="error-message">
          <p>⚠️ {error || 'Failed to load information'}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  // Directly use the API data structure - no more mock fallbacks
  const { events, weather, labor, historical } = infoData;

  return (
    <div className="info-sections">
      <div className="info-grid">
        {/* Upcoming Events */}
        <div className="info-card card">
          <div className="info-header">
            <Calendar size={20} className="info-icon" />
            <h3 className="info-title">Upcoming Events</h3>
          </div>
          <div className="events-list">
            {events?.map((event, index) => (
              <div key={index} className="event-item">
                <div className="event-date">{event.date}</div>
                <div className="event-details">
                  <span className="event-name">{event.event}</span>
                  <span className={`event-bookings ${event.bookings === 'Confirmed' ? 'confirmed' : ''}`}>
                    {event.bookings}
                  </span>
                </div>
              </div>
            ))}
          </div>
          <button className="view-all-btn">
            View All Events
            <ArrowRight size={16} />
          </button>
        </div>

        {/* Weather Impact */}
        <div className="info-card card">
          <div className="info-header">
            <Cloud size={20} className="info-icon weather" />
            <h3 className="info-title">Weather Impact</h3>
          </div>
          <div className="weather-content">
            <div className="weather-item">
              <span className="weather-label">Current</span>
              <span className="weather-value">{weather.current}</span>
            </div>
            <div className="weather-item">
              <span className="weather-label">Forecast</span>
              <span className="weather-value">{weather.forecast}</span>
            </div>
            <div className="weather-impact-box">
              <span className="impact-label">Expected Impact</span>
              <span className="impact-value">{weather.impact}</span>
            </div>
          </div>
        </div>

        {/* Historical Data */}
        <div className="info-card card">
          <div className="info-header">
            <History size={20} className="info-icon history" />
            <h3 className="info-title">Historical Comparison</h3>
          </div>
          <div className="historical-stats">
            <div className="stat-row">
              <span className="stat-label">Same Week Last Year</span>
              <span className="stat-value">{historical.lastYear}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">4-Week Average</span>
              <span className="stat-value">{historical.average}</span>
            </div>
            <div className="stat-row current">
              <span className="stat-label">This Week Projection</span>
              <span className="stat-value highlight">{historical.projection}</span>
            </div>
          </div>
        </div>

        {/* Labor Prediction */}
        <div className="info-card card labor-card">
          <div className="info-header">
            <Users size={20} className="info-icon labor" />
            <h3 className="info-title">Labor Prediction vs Planned</h3>
          </div>
          <div className="labor-content">
            <div className="labor-metrics">
              <div className="labor-metric">
                <span className="metric-label">Predicted</span>
                <span className="metric-value">{labor.predicted}</span>
                <span className="metric-unit">staff</span>
              </div>
              <div className="labor-metric">
                <span className="metric-label">Planned</span>
                <span className="metric-value">{labor.planned}</span>
                <span className="metric-unit">staff</span>
              </div>
              <div className="labor-metric variance">
                <span className="metric-label">Variance</span>
                <span className="metric-value">{labor.variance}</span>
                <span className="metric-unit">staff</span>
              </div>
            </div>
            <div className="recommendation-box">
              <span className="recommendation-label">AI Recommendation</span>
              <p className="recommendation-text">{labor.recommendation}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InfoSections;