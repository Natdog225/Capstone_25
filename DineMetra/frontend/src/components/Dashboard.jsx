// Dashboard.js - Main Dashboard Component
import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell
} from 'recharts';
import {
  TrendingUp, Users, Activity, Zap, DollarSign, ShoppingCart,
  Flag, ArrowUp, Menu, Bell, Search, ChevronDown, Layers
} from 'lucide-react';

// Individual Stat Card Component
const StatCard = ({ title, value, change, icon: Icon, color }) => {
  const [isHovered, setIsHovered] = useState(false);
  
  return (
    <div
    
      style={{
        background: 'linear-gradient(135deg, rgba(255, 185, 23, 0.1) 0%, rgba(32, 110, 182, 0.1) 100%)',
        borderRadius: '16px',
        padding: '1.5rem',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        transition: 'all 0.3s ease',
        cursor: 'pointer',
        transform: isHovered ? 'translateY(-5px)' : 'translateY(0)',
        boxShadow: isHovered ? '0 10px 30px rgba(0, 0, 0, 0.3)' : '0 4px 20px rgba(0, 0, 0, 0.2)'
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>{value}</div>
          <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.6)' }}>{title}</div>
        </div>
        <div style={{ color }}>
          <Icon size={28} strokeWidth={2.5} />
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '1rem', color: '#ffb917', fontSize: '0.875rem', fontWeight: '600' }}>
        <ArrowUp size={16} />
        <span>{change}</span>
      </div>
    </div>
  );
};

// Dashboard Header/Navbar
const DashboardHeader = () => {
  return (
    <nav style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      zIndex: 50,
      background: 'rgba(0, 0, 0, 0.8)',
      backdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
      padding: '1rem 2rem'
    }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
          <div style={{
            fontSize: '1.5rem',
            fontWeight: 'bold',
            background: 'linear-gradient(135deg, #ffb917 0%, #206EB6 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            VISION UI FREE
          </div>
          <div style={{ display: 'flex', gap: '1.5rem', color: 'rgba(255, 255, 255, 0.7)' }}>
            <a href="#dashboard" style={{ color: 'rgba(255, 255, 255, 0.7)', textDecoration: 'none', fontSize: '0.95rem', transition: 'all 0.3s ease' }}>Dashboard</a>
            <a href="#analytics" style={{ color: 'rgba(255, 255, 255, 0.7)', textDecoration: 'none', fontSize: '0.95rem', transition: 'all 0.3s ease' }}>Analytics</a>
            <a href="#reports" style={{ color: 'rgba(255, 255, 255, 0.7)', textDecoration: 'none', fontSize: '0.95rem', transition: 'all 0.3s ease' }}>Reports</a>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ position: 'relative' }}>
            <Search size={20} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'rgba(255, 255, 255, 0.5)' }} />
            <input
              type="text"
              placeholder="Search..."
              style={{
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '12px',
                padding: '0.5rem 1rem 0.5rem 2.5rem',
                color: '#ffffff',
                width: '250px',
                outline: 'none'
              }}
            />
          </div>
          <button style={{ background: 'none', border: 'none', color: '#ffffff', cursor: 'pointer', position: 'relative' }}>
            <Bell size={20} />
            <span style={{
              position: 'absolute',
              top: '-5px',
              right: '-5px',
              background: '#ffb917',
              color: '#000000',
              borderRadius: '50%',
              width: '16px',
              height: '16px',
              fontSize: '10px',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>3</span>
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #ffb917 0%, #206EB6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 'bold'
            }}>
              MJ
            </div>
            <ChevronDown size={16} />
          </div>
        </div>
      </div>
    </nav>
  );
};

// Main Chart Component
const DashboardChart = ({ data }) => {
  return (
    <div style={{
      background: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '20px',
      padding: '2rem',
      backdropFilter: 'blur(20px)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      height: '400px'
    }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>Revenue Overview</h3>
        <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.875rem' }}>Monthly performance tracking</p>
      </div>
      <ResponsiveContainer width="100%" height="85%">
        <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <defs>
            <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ffb917" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#206EB6" stopOpacity={0.2}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis dataKey="name" stroke="rgba(255,255,255,0.5)" />
          <YAxis stroke="rgba(255,255,255,0.5)" />
          <Tooltip
            contentStyle={{ background: 'rgba(0, 0, 0, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
            labelStyle={{ color: '#ffffff' }}
          />
          <Line type="monotone" dataKey="value" stroke="#ffb917" strokeWidth={3} fill="url(#revenueGradient)" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

// Country Sales Component
const CountrySalesCard = () => {
  const countryData = [
    { name: 'United States', value: 53, flag: '🇺🇸' },
    { name: 'United Kingdom', value: 19, flag: '🇬🇧' },
    { name: 'Germany', value: 15, flag: '🇩🇪' },
    { name: 'Netherlands', value: 13, flag: '🇳🇱' }
  ];

  const COLORS = ['#ffb917', '#206EB6', '#4CAF50', '#FF5722'];

  return (
    <div style={{
      background: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '20px',
      padding: '2rem',
      backdropFilter: 'blur(20px)',
      border: '1px solid rgba(255, 255, 255, 0.1)'
    }}>
      <h3 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Flag size={20} />
        Sales by Country
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {countryData.map((country, index) => (
          <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem', borderRadius: '12px', background: 'rgba(255, 255, 255, 0.03)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{ fontSize: '1.5rem' }}>{country.flag}</div>
              <div>
                <div style={{ fontWeight: '600' }}>{country.name}</div>
                <div style={{ fontSize: '0.75rem', color: 'rgba(255, 255, 255, 0.5)' }}>Region</div>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div style={{ width: '60px', height: '8px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ width: `${country.value}%`, height: '100%', background: COLORS[index] }} />
              </div>
              <span style={{ fontWeight: 'bold', minWidth: '40px' }}>{country.value}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Main Dashboard Component
const Dashboard = () => {
  const [timeRange, setTimeRange] = useState('month');

  const chartData = [
    { name: 'Jan', value: 2400 },
    { name: 'Feb', value: 1398 },
    { name: 'Mar', value: 9800 },
    { name: 'Apr', value: 3908 },
    { name: 'May', value: 4800 },
    { name: 'Jun', value: 3800 },
    { name: 'Jul', value: 4300 }
  ];

  const stats = [
    { title: 'Total Revenue', value: '$53,000', change: '+55%', icon: DollarSign, color: '#4CAF50' },
    { title: 'Total Users', value: '2,300', change: '+5%', icon: Users, color: '#206EB6' },
    { title: 'Daily Users', value: '3,052', change: '+3%', icon: Activity, color: '#ffb917' },
    { title: 'Total Sales', value: '$173,000', change: '+8%', icon: TrendingUp, color: '#FF5722' }
  ];

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #000000 0%, #206EB6 50%, #000000 100%)',
      color: '#ffffff',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      paddingTop: '100px'
    }}>
      <DashboardHeader />
      
      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '2rem' }}>
        {/* Stats Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          {stats.map((stat, index) => (
            <StatCard key={index} {...stat} />
          ))}
        </div>

        {/* Time Range Selector */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '12px', padding: '0.25rem' }}>
            {['week', 'month', 'year'].map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                style={{
                  padding: '0.5rem 1rem',
                  borderRadius: '8px',
                  border: 'none',
                  background: timeRange === range ? 'linear-gradient(135deg, #ffb917 0%, #206EB6 100%)' : 'transparent',
                  color: '#ffffff',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}
              >
                {range.charAt(0).toUpperCase() + range.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Main Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
          <DashboardChart data={chartData} />
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ background: 'rgba(255, 255, 255, 0.05)', borderRadius: '16px', padding: '1.5rem', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <div>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>9.3%</div>
                  <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.6)' }}>Active Users</div>
                </div>
                <Activity size={24} style={{ color: '#ffb917' }} />
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#4CAF50', fontSize: '0.875rem' }}>
                <ArrowUp size={16} />
                <span>+5% from last week</span>
              </div>
            </div>

            <div style={{ background: 'rgba(255, 255, 255, 0.05)', borderRadius: '16px', padding: '1.5rem', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <div>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>145</div>
                  <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.6)' }}>Projects</div>
                </div>
                <Layers size={24} style={{ color: '#206EB6' }} />
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#ffb917', fontSize: '0.875rem' }}>
                <ArrowUp size={16} />
                <span>+5 new this month</span>
              </div>
            </div>

            <div style={{ background: 'rgba(255, 255, 255, 0.05)', borderRadius: '16px', padding: '1.5rem', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <div>
                  <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>1,445</div>
                  <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.6)' }}>Orders overview</div>
                </div>
                <ShoppingCart size={24} style={{ color: '#FF5722' }} />
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#4CAF50', fontSize: '0.875rem' }}>
                <ArrowUp size={16} />
                <span>+1% from last week</span>
              </div>
            </div>
          </div>
        </div>

        {/* Countries Section */}
        <CountrySalesCard />
      </div>
    </div>
  );
};

export default Dashboard;