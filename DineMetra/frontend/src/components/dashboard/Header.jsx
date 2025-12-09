import React from 'react';
import { LogOut, Menu } from 'lucide-react';
import './CSS/Header.css';

const Header = ({ onLogout, onMenuClick }) => {
  return (
    <header className="dashboard-header">
      <div className="header-content">
        <div className="header-left">
          <button 
            className="hamburger-menu" 
            onMouseEnter={onMenuClick}
            aria-label="Open menu"
          >
            <Menu size={24} />
          </button>
        </div>
        
        <img 
          src="/DineMetra_Logo.png" 
          alt="DineMetra Logo" 
          className="header-logo" 
          loading="eager"
        />
        
        <div className="header-right">
          <button 
            onClick={onLogout}
            className="logout-button"
            aria-label="Logout"
          >
            <LogOut size={18} />
            <span>Logout</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;