import React from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  History, 
  Brain, 
  X 
} from 'lucide-react';
import './CSS/Sidebar.css';

const Sidebar = ({ isOpen, onClose, activeTab, onTabChange }) => {
  const menuItems = [
    { id: 'sales-overview', label: 'Sales Overview', icon: BarChart3 },
    { id: 'sales-metrics', label: 'Sales Metrics', icon: TrendingUp },
    { id: 'historical-analysis', label: 'Historical Analysis', icon: History },
    { id: 'ai-predictions', label: 'Daily AI Predictions', icon: Brain }
  ];

  const handleTabClick = (tabId) => {
    onTabChange(tabId);
    onClose(); // Close sidebar after selection
  };

  return (
    <>
      {/* Overlay */}
      <div 
        className={`sidebar-overlay ${isOpen ? 'active' : ''}`}
        onClick={onClose}
      />
      
      {/* Sidebar */}
      <aside 
        className={`sidebar ${isOpen ? 'open' : ''}`}
        onMouseLeave={onClose}
      >
        <div className="sidebar-header">
          <h2 className="sidebar-title">Navigation</h2>
          <button className="sidebar-close" onClick={onClose}>
            <X size={24} />
          </button>
        </div>
        
        <nav className="sidebar-nav">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                className={`sidebar-nav-item ${activeTab === item.id ? 'active' : ''}`}
                onClick={() => handleTabClick(item.id)}
              >
                <Icon size={20} className="nav-icon" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>
    </>
  );
};

export default Sidebar;