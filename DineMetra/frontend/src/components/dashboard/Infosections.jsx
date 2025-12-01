import React from 'react';
import { Calendar, Cloud, History, Users, ArrowRight } from 'lucide-react';
import './CSS/Infosections.css';

const InfoSections = ({ infoData = {} }) => {
  const defaultData = {
    events: [
      { date: 'Nov 28', event: 'Thanksgiving Special Menu', bookings: '85%' },
      { date: 'Dec 5', event: 'Wine Tasting Event', bookings: '60%' },
      { date: 'Dec 15', event: 'Holiday Party - Private', bookings: 'Confirmed' },
    ],
    weather: {
      current: 'Clear skies expected',
      forecast: 'Weekend: 30% rain chance',
      impact: 'Moderate patio seating impact'
    },
    labor: {
      predicted: 32,
      planned: 30,
      variance: '+2',
      recommendation: 'Consider adding 1 server for Saturday peak'
    },
    historical: {
      lastYear: '$42,500',
      average: '$38,750',
      projection: '$41,200'
    }
  };

  const upcomingEvents = infoData.events || defaultData.events;
  const weatherImpact = infoData.weather || defaultData.weather;
  const laborPrediction = infoData.labor || defaultData.labor;
  const historicalData = infoData.historical || defaultData.historical;

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
            {upcomingEvents.map((event, index) => (
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
              <span className="weather-value">{weatherImpact.current}</span>
            </div>
            <div className="weather-item">
              <span className="weather-label">Forecast</span>
              <span className="weather-value">{weatherImpact.forecast}</span>
            </div>
            <div className="weather-impact-box">
              <span className="impact-label">Expected Impact</span>
              <span className="impact-value">{weatherImpact.impact}</span>
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
              <span className="stat-value">{historicalData.lastYear}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">4-Week Average</span>
              <span className="stat-value">{historicalData.average}</span>
            </div>
            <div className="stat-row current">
              <span className="stat-label">This Week Projection</span>
              <span className="stat-value highlight">{historicalData.projection}</span>
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
                <span className="metric-value">{laborPrediction.predicted}</span>
                <span className="metric-unit">staff</span>
              </div>
              <div className="labor-metric">
                <span className="metric-label">Planned</span>
                <span className="metric-value">{laborPrediction.planned}</span>
                <span className="metric-unit">staff</span>
              </div>
              <div className="labor-metric variance">
                <span className="metric-label">Variance</span>
                <span className="metric-value">{laborPrediction.variance}</span>
                <span className="metric-unit">staff</span>
              </div>
            </div>
            <div className="recommendation-box">
              <span className="recommendation-label">AI Recommendation</span>
              <p className="recommendation-text">{laborPrediction.recommendation}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InfoSections;