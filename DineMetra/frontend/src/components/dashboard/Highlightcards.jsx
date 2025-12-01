import React from 'react';
import { AlertCircle } from 'lucide-react';
import './CSS/Highlightcards.css';

const HighlightCards = ({ highlights = [] }) => {
  console.log('Raw highlights data:', highlights);

  // FILTER: Exclude items with specific keywords (case-insensitive)
  const excludedKeywords = ['SKY CLUB', 'SUITES', 'UPCHARGE', 'CLUB SEATS'];
  const filteredHighlights = highlights.filter(highlight => {
    const searchableText = `${highlight.details} ${highlight.subDetails}`.toUpperCase();
    return !excludedKeywords.some(keyword => searchableText.includes(keyword));
  });

  // SORT: By importance (high → medium → low)
  const importanceOrder = { high: 0, medium: 1, low: 2 };
  const sortedHighlights = [...filteredHighlights].sort((a, b) => {
    const aLevel = a.importance || 'medium';
    const bLevel = b.importance || 'medium';
    return importanceOrder[aLevel] - importanceOrder[bLevel];
  });

  console.log('Filtered & sorted highlights:', sortedHighlights);

  // Default mock data if API returns nothing
  const defaultHighlights = sortedHighlights.length > 0 ? sortedHighlights : [
    {
      id: 1,
      title: 'Big Event',
      icon: 'Calendar',
      color: 'blue',
      details: 'Jazz Night - Saturday',
      subDetails: 'Expected: 150+ guests',
      date: '2025-12-07',
      importance: 'high'
    }
  ];

  const renderIcon = (iconName) => {
    const icons = {
      Calendar: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>,
      CloudRain: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"></path><line x1="16" y1="13" x2="16" y2="21"></line><line x1="8" y1="13" x2="8" y2="21"></line><line x1="12" y1="15" x2="12" y2="23"></line></svg>,
      Tag: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7" y2="7"></line></svg>,
    };
    return icons[iconName] || null;
  };

  return (
    <div className="highlight-cards">
      <div className="highlights-header">
        <h2 className="section-title">This Week's Highlights</h2>
        <AlertCircle size={18} className="info-icon" />
      </div>
      
      <div className="cards-grid">
        {defaultHighlights.map((highlight) => (
          <div key={highlight.id} className={`highlight-card ${highlight.color || 'blue'} ${highlight.importance || 'medium'}`}>
            <div className="card-icon-wrapper">
              {renderIcon(highlight.icon)}
            </div>
            <div className="card-content">
              <h3 className="card-title">{highlight.title}</h3>
              <p className="card-details">{highlight.details}</p>
              <p className="card-sub-details">{highlight.subDetails}</p>
              <p className="card-date">{highlight.date}</p>
            </div>
            {highlight.importance === 'high' && (
              <div className="importance-badge">High Priority</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default HighlightCards;