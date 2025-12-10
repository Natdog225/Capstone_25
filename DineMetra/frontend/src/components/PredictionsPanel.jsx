import React, { useState } from 'react';
import { Clock, TrendingUp, ShoppingCart, RefreshCw, ChevronDown } from 'lucide-react';
import { usePredictions } from '../hooks/usePredictions';
import './dashboard/CSS/PredictionPanel.css';


const PredictionsPanel = () => {
  const { predictions, loading, errors, refreshPrediction, refreshAll } = usePredictions();
  const isAnyLoading = Object.values(loading).some(Boolean);

  return (
    <div className="predictions-panel card fade-in">
      <div className="panel-header">
        <h2 className="section-title">AI Predictions</h2>
        <button onClick={refreshAll} disabled={isAnyLoading} className="refresh-btn">
          <RefreshCw size={16} className={isAnyLoading ? 'spinning' : ''} />
          {isAnyLoading ? 'Loading...' : 'Refresh All'}
        </button>
      </div>

      <div className="predictions-grid">
        <PredictionCard icon={<Clock size={24} />} title="Wait Time" onPredict={() => refreshPrediction('waitTime', 4)} loading={loading.waitTime} data={predictions.waitTime} error={errors.waitTime} renderData={(data) => <WaitTimeDisplay data={data} />} />
        <PredictionCard icon={<TrendingUp size={24} />} title="Busyness Level" onPredict={() => refreshPrediction('busyness')} loading={loading.busyness} data={predictions.busyness} error={errors.busyness} renderData={(data) => <BusynessDisplay data={data} />} />
        <PredictionCard icon={<ShoppingCart size={24} />} title="Sales Forecast" onPredict={() => refreshPrediction('sales', 101, null, 'Burger Special', 'Entrees')} loading={loading.sales} data={predictions.sales} error={errors.sales} renderData={(data) => <SalesDisplay data={data} />} />
      </div>
    </div>
  );
};

// Separate display components for each prediction type
const WaitTimeDisplay = ({ data }) => {
  if (!data) return null;
  return (
    <div className="prediction-display">
      <div className="main-value">
        <span className="value-number">{data.predicted_wait_minutes ?? '--'}</span>
        <span className="value-unit">min</span>
      </div>
      <div className="confidence-indicator">
        <span className="confidence-label">Confidence</span>
        <span className="confidence-score">{((data.confidence ?? 0) * 100).toFixed(0)}%</span>
      </div>
      {data.factors && <FactorsList factors={data.factors} title="Key Factors" />}
    </div>
  );
};

const BusynessDisplay = ({ data }) => {
  if (!data) return null;
  const level = data.level || data.busyness_label || 'Unknown';
  const percentage = data.percentage || data.busyness_score || 0;
  const expectedGuests = data.expected_guests || data.expected_guests_count;
  const recommendation = data.recommendation || data.staffing_recommendation;

  return (
    <div className="prediction-display">
      <div className="busyness-header">
        <div className="busyness-level-badge" data-level={level.toLowerCase()}>{level}</div>
        <div className="busyness-percentage">{Math.round(percentage)}%</div>
      </div>
      <div className="busyness-gauge-container">
        <div className="busyness-gauge">
          <div className="busyness-fill" style={{ height: `${percentage}%` }} />
        </div>
        <div className="busyness-details">
          {expectedGuests && <div className="detail-row"><span className="detail-label">Expected Guests</span><span className="detail-value">{expectedGuests}</span></div>}
          {data.confidence && <div className="detail-row"><span className="detail-label">Confidence</span><span className="detail-value">{((data.confidence ?? 0) * 100).toFixed(0)}%</span></div>}
        </div>
      </div>
      {recommendation && <div className="recommendation-box"><span className="recommendation-icon">💡</span><span className="recommendation-text">{recommendation}</span></div>}
      {data.factors && <FactorsList factors={data.factors} title="Impact Factors" />}
    </div>
  );
};

const SalesDisplay = ({ data }) => {
  if (!data) return null;
  return (
    <div className="prediction-display">
      <div className="main-value">
        <span className="value-number">{data.predicted_quantity ?? '--'}</span>
        <span className="value-unit">units</span>
      </div>
      <div className="sales-details">
        {data.margin && <div className="margin-range"><span className="range-label">Range</span><span className="range-values">{data.margin.low}-{data.margin.high} units</span></div>}
        <div className="confidence-indicator"><span className="confidence-label">Confidence</span><span className="confidence-score">{((data.confidence ?? 0) * 100).toFixed(0)}%</span></div>
        {data.price && <div className="revenue-estimate">Est. Revenue: ${((data.predicted_quantity ?? 0) * data.price).toFixed(2)}</div>}
      </div>
      {data.factors && <FactorsList factors={data.factors} title="Sales Factors" />}
    </div>
  );
};

// Reusable factors list with smooth toggle
const FactorsList = ({ factors, title }) => {
  const [isOpen, setIsOpen] = useState(false);
  if (!factors || Object.keys(factors).length === 0) return null;
  
  const simpleFactors = Object.entries(factors).filter(([_, value]) => typeof value !== 'object' && !Array.isArray(value));

  return (
    <div className="factors-section">
      <button className={`factors-toggle ${isOpen ? 'open' : ''}`} onClick={() => setIsOpen(!isOpen)}>
        <ChevronDown size={16} className="toggle-icon" />
        <span>{title} ({simpleFactors.length})</span>
      </button>
      {isOpen && (
        <div className="factors-list">
          {simpleFactors.map(([key, value]) => (
            <div key={key} className="factor-item">
              <span className="factor-name">{formatFactorName(key)}</span>
              <span className="factor-value">{formatFactorValue(value)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Helper formatters
const formatFactorName = (key) => key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
const formatFactorValue = (value) => {
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (typeof value === 'number') {
    if (value > 100) return value.toLocaleString();
    if (value < 1 && value > 0) return `${(value * 100).toFixed(0)}%`;
    return value.toString();
  }
  return value;
};

// Card wrapper component
const PredictionCard = ({ icon, title, onPredict, loading, data, error, renderData }) => {
  const shouldRenderData = data && !loading;
  return (
    <div className="prediction-card">
      <div className="card-header">{icon}<h3>{title}</h3></div>
      <button onClick={onPredict} disabled={loading} className="predict-btn">{loading ? 'Loading...' : `Get ${title}`}</button>
      <div className="result-container">
        {loading && <div className="skeleton-loader" />}
        {shouldRenderData && <div className="result">{renderData(data)}</div>}
        {error && !loading && <p className="error">{error}</p>}
        {!shouldRenderData && !error && !loading && <p className="info">Click button to load prediction</p>}
      </div>
    </div>
  );
};

export default PredictionsPanel;