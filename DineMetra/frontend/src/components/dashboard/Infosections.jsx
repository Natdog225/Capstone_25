import React, { useState, useEffect } from 'react';
import { Calendar, History, Users, ArrowRight, X } from 'lucide-react';
import { dinemetraAPI } from '../../services/dinemetraService.js';
import './CSS/Infosections.css';
import HistoricalComparison from './HistoricalComparison.jsx';

// Import weather icons
import { 
  WiDaySunny, 
  WiCloud, 
  WiRain, 
  WiThunderstorm, 
  WiSnow, 
  WiDayCloudy, 
  WiFog, 
  WiStrongWind 
} from 'react-icons/wi';

const InfoSections = () => {
  const [infoData, setInfoData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAllEvents, setShowAllEvents] = useState(false);
  const [allEvents, setAllEvents] = useState([]);

  useEffect(() => {
    const fetchInfoSections = async () => {
      try {
        setLoading(true);
        const data = await dinemetraAPI.getInfoSections();
        console.log('InfoSections - Raw API data:', data);

        // Process events: filter and sort
        if (data?.events) {
          const excludedKeywords = ['SKY CLUB', 'SUITES', 'UPCHARGE', 'CLUB SEATS'];
          
          const filteredEvents = data.events.filter(event => {
            const searchableText = `${event.event || ''} ${event.subDetails || ''}`.toUpperCase();
            return !excludedKeywords.some(keyword => searchableText.includes(keyword));
          });
          
          console.log(`InfoSections - Filtered out ${data.events.length - filteredEvents.length} events`);
          
          const importanceOrder = { high: 0, medium: 1, low: 2 };
          const sortedEvents = [...filteredEvents].sort((a, b) => {
            if (!a.importance && !b.importance) return 0;
            const aLevel = a.importance || 'medium';
            const bLevel = b.importance || 'medium';
            return importanceOrder[aLevel] - importanceOrder[bLevel];
          });
          
          data.events = sortedEvents;
        }
        
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

  // Load 60-day events when button clicked
  const handleViewAllEvents = async () => {
    try {
      const events = await dinemetraAPI.getAllEvents(60);
      setAllEvents(events);
      setShowAllEvents(true);
    } catch (err) {
      console.error('Failed to load all events:', err);
    }
  };

  // Helper to map weather conditions to icons
  const getWeatherIcon = (condition, size = 32) => {
    const conditionLower = condition?.toLowerCase() || '';
    
    if (conditionLower.includes('sun') || conditionLower.includes('clear')) {
      return <WiDaySunny size={size} color="#FFA500" />;
    }
    if (conditionLower.includes('snow')) {
      return <WiSnow size={size} color="#87CEEB" />;
    }
    if (conditionLower.includes('thunder') || conditionLower.includes('storm')) {
      return <WiThunderstorm size={size} color="#4B0082" />;
    }
    if (conditionLower.includes('rain')) {
      return <WiRain size={size} color="#4682B4" />;
    }
    if (conditionLower.includes('cloud')) {
      return conditionLower.includes('partly') ? 
        <WiDayCloudy size={size} color="#708090" /> : 
        <WiCloud size={size} color="#696969" />;
    }
    if (conditionLower.includes('fog') || conditionLower.includes('haze')) {
      return <WiFog size={size} color="#808080" />;
    }
    if (conditionLower.includes('wind')) {
      return <WiStrongWind size={size} color="#708090" />;
    }
    
    return <WiCloud size={size} color="#708090" />;
  };

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
                  {event.subDetails && (
                    <span className="event-sub-details">{event.subDetails}</span>
                  )}
                  <span className={`event-bookings ${event.bookings === 'Confirmed' ? 'confirmed' : ''}`}>
                    {event.bookings}
                  </span>
                </div>
              </div>
            ))}
          </div>
          <button className="view-all-btn" onClick={handleViewAllEvents}>
            View All Events (60 Days)
            <ArrowRight size={16} />
          </button>
        </div>

        {/* Weather Impact */}
        <div className="info-card card">
          <div className="info-header">
            <div className="weather-icon-wrapper">
              {getWeatherIcon(weather.current, 32)}
            </div>
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

        {/* Historical Comparison - NEW SEPARATE COMPONENT */}
        <HistoricalComparison historical={historical} />

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

      {/* Modal for all events */}
      {showAllEvents && (
        <div className="modal-overlay" onClick={() => setShowAllEvents(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Upcoming Events (Next 60 Days)</h2>
              <button className="modal-close" onClick={() => setShowAllEvents(false)}>
                <X size={24} />
              </button>
            </div>
            <div className="modal-body">
              <div className="events-list">
                {allEvents.map((event) => (
                  <div key={event.id} className="event-item">
                    <div className="event-date">{event.date}</div>
                    <div className="event-details">
                      <span className="event-name">{event.event}</span>
                      {event.subDetails && (
                        <span className="event-sub-details">{event.subDetails}</span>
                      )}
                      <span className={`event-importance ${event.importance}`}>
                        {event.importance}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="modal-footer">
              <button className="modal-back-btn" onClick={() => setShowAllEvents(false)}>
                Back
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InfoSections;