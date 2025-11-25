import React from 'react';
import { Calendar, CloudRain, Tag, AlertCircle } from 'lucide-react';
import './CSS/Highlightcards.css';

const HighlightCards = () => {
  const highlights = [
    {
      id: 1,
      title: 'Big Event',
      icon: Calendar,
      color: 'blue',
      details: 'Jazz Night - Saturday',
      subDetails: 'Expected: 150+ guests',
      importance: 'high'
    },
    {
      id: 2,
      title: 'Weather Alert',
      icon: CloudRain,
      color: 'orange',
      details: 'Rain 90% Saturday',
      subDetails: 'Prepare indoor seating',
      importance: 'high'
    },
    {
      id: 3,
      title: 'Active Promo',
      icon: Tag,
      color: 'green',
      details: 'Happy Hour Extended',
      subDetails: '45% off selected drinks',
      importance: 'medium'
    }
  ];

  return (
    <div className="highlight-cards">
      <div className="highlights-header">
        <h2 className="section-title">This Week's Highlights</h2>
        <AlertCircle size={18} className="info-icon" />
      </div>
      
      <div className="cards-grid">
        {highlights.map((highlight) => {
          const Icon = highlight.icon;
          return (
            <div 
              key={highlight.id} 
              className={`highlight-card ${highlight.color} ${highlight.importance}`}
            >
              <div className="card-icon-wrapper">
                <Icon size={24} className="card-icon" />
              </div>
              <div className="card-content">
                <h3 className="card-title">{highlight.title}</h3>
                <p className="card-details">{highlight.details}</p>
                <p className="card-sub-details">{highlight.subDetails}</p>
              </div>
              {highlight.importance === 'high' && (
                <div className="importance-badge">High Priority</div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default HighlightCards;