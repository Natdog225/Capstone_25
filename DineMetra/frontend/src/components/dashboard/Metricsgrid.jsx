import React from 'react';
import { ShoppingCart, Wine, Beer, DollarSign, Users, TrendingUp } from 'lucide-react';
import './CSS/Metricsgrid.css';

const MetricsGrid = () => {
  const metrics = [
    {
      id: 1,
      title: 'Best Sellers',
      icon: ShoppingCart,
      items: [
        { name: 'Burger Special', value: '156', trend: 'up' },
        { name: 'Fish Tacos', value: '132', trend: 'up' },
        { name: 'Caesar Salad', value: '98', trend: 'down' },
      ]
    },
    {
      id: 2,
      title: 'Bar Drinks',
      icon: Wine,
      items: [
        { name: 'Cocktails', value: '245', trend: 'up' },
        { name: 'Wine', value: '189', trend: 'stable' },
        { name: 'Spirits', value: '156', trend: 'up' },
      ]
    },
    {
      id: 3,
      title: 'Top Beers',
      icon: Beer,
      items: [
        { name: 'IPA Draft', value: '98', trend: 'up' },
        { name: 'Lager', value: '76', trend: 'stable' },
        { name: 'Stout', value: '54', trend: 'down' },
      ]
    },
    {
      id: 4,
      title: 'Labor Cost',
      icon: Users,
      percentage: '28.5%',
      target: '30%',
      status: 'good',
      details: 'Within target range'
    },
    {
      id: 5,
      title: 'Actual vs Expected',
      icon: TrendingUp,
      percentage: '104%',
      variance: '+$4,200',
      status: 'excellent',
      details: 'Exceeding projections'
    }
  ];

  const purchasingEstimates = [
    { item: 'Produce', estimate: '$1,850', status: 'Order Today' },
    { item: 'Meat/Seafood', estimate: '$2,400', status: 'Order Tomorrow' },
    { item: 'Bar Supplies', estimate: '$980', status: 'Stock OK' }
  ];

  return (
    <div className="metrics-section">
      <div className="metrics-header">
        <h2 className="section-title">30 Day Average</h2>
        <span className="date-range">Oct 26 - Nov 25</span>
      </div>

      <div className="metrics-grid">
        {metrics.slice(0, 3).map((metric) => {
          const Icon = metric.icon;
          return (
            <div key={metric.id} className="metric-card card">
              <div className="metric-card-header">
                <Icon size={20} className="metric-icon" />
                <h3 className="metric-title">{metric.title}</h3>
              </div>
              <div className="metric-items">
                {metric.items.map((item, index) => (
                  <div key={index} className="metric-item">
                    <span className="item-name">{item.name}</span>
                    <div className="item-value-wrapper">
                      <span className="item-value">{item.value}</span>
                      {item.trend === 'up' && <span className="trend-indicator up">↑</span>}
                      {item.trend === 'down' && <span className="trend-indicator down">↓</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      <div className="secondary-metrics">
        {metrics.slice(3).map((metric) => {
          const Icon = metric.icon;
          return (
            <div key={metric.id} className={`metric-highlight card ${metric.status}`}>
              <div className="highlight-header">
                <Icon size={20} className="metric-icon" />
                <h3 className="metric-title">{metric.title}</h3>
              </div>
              <div className="highlight-value">{metric.percentage}</div>
              {metric.target && (
                <div className="highlight-target">Target: {metric.target}</div>
              )}
              {metric.variance && (
                <div className="highlight-variance">{metric.variance}</div>
              )}
              <div className="highlight-details">{metric.details}</div>
            </div>
          );
        })}
      </div>

      <div className="purchasing-section card">
        <h3 className="section-title">Purchasing Estimates</h3>
        <div className="purchasing-grid">
          {purchasingEstimates.map((item, index) => (
            <div key={index} className="purchasing-item">
              <div className="purchasing-info">
                <span className="purchasing-name">{item.item}</span>
                <span className="purchasing-estimate">{item.estimate}</span>
              </div>
              <span className={`purchasing-status ${item.status.toLowerCase().replace(' ', '-')}`}>
                {item.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MetricsGrid;