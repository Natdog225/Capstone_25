import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import {
  ChevronRight, Zap, Shield, TrendingUp, Users, Activity,
  Layers, Award, ArrowUp, Menu, X, Star, Check
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const VisionUILanding = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [activeMetric, setActiveMetric] = useState(0);
  const navigate = useNavigate();

  const lineData = [
    { name: 'Jan', value: 2400 },
    { name: 'Feb', value: 1398 },
    { name: 'Mar', value: 9800 },
    { name: 'Apr', value: 3908 },
    { name: 'May', value: 4800 },
    { name: 'Jun', value: 3800 },
    { name: 'Jul', value: 4300 }
  ];

  const metrics = [
    { value: '$53,000', label: 'Total Revenue', change: '+55%', icon: TrendingUp },
    { value: '2,300', label: 'Total Users', change: '+5%', icon: Users },
    { value: '3,052', label: 'New Orders', change: '+14%', icon: Activity },
    { value: '$173,000', label: 'Total Sales', change: '+8%', icon: Zap }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveMetric((prev) => (prev + 1) % metrics.length);
    }, 3000);
    return () => clearInterval(interval);
  }, [metrics]);

  const styles = {
    container: {
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #000000 0%, #206EB6 50%, #000000 100%)',
      color: '#ffffff',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      overflow: 'hidden',
      position: 'relative'
    },
    backgroundEffects: {
      position: 'absolute',
      width: '100%',
      height: '100%',
      top: 0,
      left: 0,
      pointerEvents: 'none',
      overflow: 'hidden'
    },
    glowOrb: {
      position: 'absolute',
      borderRadius: '50%',
      filter: 'blur(100px)',
      opacity: 0.3
    },
    navbar: {
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      zIndex: 50,
      background: 'rgba(0, 0, 0, 0.8)',
      backdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
    },
    navContent: {
      maxWidth: '1280px',
      margin: '0 auto',
      padding: '1rem 2rem',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    },
    logo: {
      fontSize: '1.5rem',
      fontWeight: 'bold',
      background: 'linear-gradient(135deg, #ffb917 0%, #206EB6 100%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem'
    },
    navLinks: {
      display: 'flex',
      gap: '2rem',
      alignItems: 'center'
    },
    navLink: {
      color: 'rgba(255, 255, 255, 0.7)',
      textDecoration: 'none',
      fontSize: '0.95rem',
      transition: 'all 0.3s ease',
      cursor: 'pointer'
    },
    heroSection: {
      paddingTop: '120px',
      paddingBottom: '80px',
      position: 'relative',
      zIndex: 10
    },
    heroContent: {
      maxWidth: '1280px',
      margin: '0 auto',
      padding: '0 2rem',
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: '4rem',
      alignItems: 'center'
    },
    heroText: {
      animation: 'slideInLeft 1s ease-out'
    },
    heroTitle: {
      fontSize: '3.5rem',
      fontWeight: 'bold',
      lineHeight: 1.2,
      marginBottom: '1.5rem',
      background: 'linear-gradient(135deg, #ffffff 0%, #ffb917 50%, #206EB6 100%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent'
    },
    heroSubtitle: {
      fontSize: '1.25rem',
      color: 'rgba(255, 255, 255, 0.7)',
      marginBottom: '2rem',
      lineHeight: 1.6
    },
    ctaButtons: {
      display: 'flex',
      gap: '1rem',
      marginBottom: '3rem'
    },
    primaryButton: {
      padding: '0.75rem 2rem',
      background: 'linear-gradient(135deg, #ffb917 0%, #206EB6 100%)',
      border: 'none',
      borderRadius: '12px',
      color: '#ffffff',
      fontSize: '1rem',
      fontWeight: '600',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      transition: 'all 0.3s ease',
      boxShadow: '0 4px 20px rgba(255, 185, 23, 0.3)'
    },
    secondaryButton: {
      padding: '0.75rem 2rem',
      background: 'rgba(255, 255, 255, 0.1)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      borderRadius: '12px',
      color: '#ffffff',
      fontSize: '1rem',
      fontWeight: '600',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      backdropFilter: 'blur(10px)'
    },
    dashboardPreview: {
      position: 'relative',
      background: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '20px',
      padding: '2rem',
      backdropFilter: 'blur(20px)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
      animation: 'slideInRight 1s ease-out'
    },
    miniCard: {
      background: 'linear-gradient(135deg, rgba(255, 185, 23, 0.1) 0%, rgba(32, 110, 182, 0.1) 100%)',
      borderRadius: '16px',
      padding: '1.5rem',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      marginBottom: '1rem'
    },
    metricValue: {
      fontSize: '2rem',
      fontWeight: 'bold',
      marginBottom: '0.5rem'
    },
    metricLabel: {
      fontSize: '0.875rem',
      color: 'rgba(255, 255, 255, 0.6)'
    },
    featureIcon: {
      width: '60px',
      height: '60px',
      background: 'linear-gradient(135deg, #ffb917 0%, #206EB6 100%)',
      borderRadius: '16px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      marginBottom: '1.5rem'
    },
    statNumber: {
      fontSize: '3rem',
      fontWeight: 'bold',
      background: 'linear-gradient(135deg, #ffb917 0%, #206EB6 100%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent'
    },
    // Keep other styles mostly unchanged
  };

  return (
    <div style={styles.container}>
      {/* Background Effects */}
      <div style={styles.backgroundEffects}>
        <div style={{...styles.glowOrb, width: '600px', height: '600px', top: '-200px', left: '-200px', background: 'radial-gradient(circle, #ffb917 0%, transparent 70%)'}} />
        <div style={{...styles.glowOrb, width: '800px', height: '800px', bottom: '-300px', right: '-300px', background: 'radial-gradient(circle, #206EB6 0%, transparent 70%)'}} />
      </div>

      {/* Navigation */}
      <nav style={styles.navbar}>
        <div style={styles.navContent}>
          <div style={styles.logo}>
            <Layers size={28} />
            Vision UI
          </div>
          <div style={{...styles.navLinks, display: window.innerWidth > 768 ? 'flex' : 'none'}}>
            <a href="#features" style={styles.navLink}>Features</a>
            <a href="#dashboard" style={styles.navLink}>Dashboard</a>
            <a href="#pricing" style={styles.navLink}>Pricing</a>
            <a href="#about" style={styles.navLink}>About</a>
            <button 
                style={styles.primaryButton} 
                onClick={() => navigate('/dashboard')}
            >
                Get Started
            </button>
          </div>
            <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            style={styles.mobileMenuButton}
            onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                e.currentTarget.style.transform = 'scale(1.1)';
            }}
            onMouseLeave={(e) => {
                e.currentTarget.style.background = 'none';
                e.currentTarget.style.transform = 'scale(1)';
            }}
            aria-label="Toggle navigation menu"
            aria-expanded={isMenuOpen}
            >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section style={styles.heroSection}>
        <div style={styles.heroContent}>
          <div style={styles.heroText}>
            <h1 style={styles.heroTitle}>
              The Future of Dashboard Design
            </h1>
            <p style={styles.heroSubtitle}>
              Experience the most beautiful and functional admin dashboard. Built with React, powered by innovation.
            </p>
            <div style={styles.ctaButtons}>
              <button style={styles.primaryButton}>
                Start Free Trial
                <ChevronRight size={20} />
              </button>
              <button style={styles.secondaryButton}>
                View Demo
              </button>
            </div>
            <div style={{display: 'flex', gap: '3rem', color: 'rgba(255, 255, 255, 0.6)'}}>
              <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                <Star size={20} style={{color: '#ffb917'}} />
                <span>4.9/5 Rating</span>
              </div>
              <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                <Users size={20} />
                <span>10k+ Users</span>
              </div>
              <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                <Award size={20} />
                <span>Award Winning</span>
              </div>
            </div>
          </div>
          <div style={styles.dashboardPreview}>
            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem'}}>
              {metrics.map((metric, index) => (
                <div
                  key={index}
                  style={{
                    ...styles.miniCard,
                    opacity: activeMetric === index ? 1 : 0.7,
                    transform: activeMetric === index ? 'scale(1.02)' : 'scale(1)',
                    transition: 'all 0.3s ease'
                  }}
                >
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'start'}}>
                    <div>
                      <div style={styles.metricValue}>{metric.value}</div>
                      <div style={styles.metricLabel}>{metric.label}</div>
                    </div>
                    <div style={{color: '#ffb917'}}>
                      <metric.icon size={24} />
                    </div>
                  </div>
                  <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.5rem', color: '#ffb917', fontSize: '0.875rem'}}>
                    <ArrowUp size={16} />
                    {metric.change}
                  </div>
                </div>
              ))}
            </div>
            <div style={{...styles.miniCard, height: '200px'}}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={lineData}>
                  <defs>
                    <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ffb917" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#206EB6" stopOpacity={0.2}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="name" stroke="rgba(255,255,255,0.5)" />
                  <YAxis stroke="rgba(255,255,255,0.5)" />
                  <Tooltip
                    contentStyle={{background: 'rgba(0, 0, 0, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px'}}
                    labelStyle={{color: '#ffffff'}}
                  />
                  <Line type="monotone" dataKey="value" stroke="#ffb917" strokeWidth={3} fill="url(#colorGradient)" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
<section id="features" style={{padding: '6rem 2rem', backgroundColor: '#000000', color: '#ffffff'}}>
  <div style={{maxWidth: '1280px', margin: '0 auto', textAlign: 'center'}}>
    <h2 style={{fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '1rem', background: 'linear-gradient(135deg, #ffb917 0%, #206EB6 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'}}>
      Features That Empower You
    </h2>
    <p style={{color: 'rgba(255,255,255,0.7)', marginBottom: '4rem', fontSize: '1.1rem'}}>
      Everything you need in one dashboard: insights, metrics, analytics, and controls.
    </p>
    <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem'}}>
      {[
        {icon: Shield, title: 'Secure', desc: 'End-to-end encryption and robust security controls.'},
        {icon: Zap, title: 'Fast', desc: 'Lightning fast performance and data processing.'},
        {icon: TrendingUp, title: 'Insights', desc: 'Deep analytics to drive smarter decisions.'},
        {icon: Users, title: 'Collaboration', desc: 'Built for teams to work together seamlessly.'},
        {icon: Layers, title: 'Customizable', desc: 'Flexible layouts, themes, and widgets.'},
        {icon: Activity, title: 'Real-Time', desc: 'Live updates to keep you always informed.'}
      ].map((feature, index) => (
        <div key={index} style={{
          background: 'rgba(255,255,255,0.05)',
          padding: '2rem',
          borderRadius: '16px',
          border: '1px solid rgba(255,255,255,0.1)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
          transition: 'all 0.3s ease',
          cursor: 'default'
        }}>
          <div style={{
            ...styles.featureIcon,
            background: 'linear-gradient(135deg, #ffb917 0%, #206EB6 100%)'
          }}>
            <feature.icon size={32} color="#ffffff"/>
          </div>
          <h3 style={{margin: '1rem 0 0.5rem', fontSize: '1.25rem', fontWeight: '600'}}>{feature.title}</h3>
          <p style={{color: 'rgba(255,255,255,0.7)', fontSize: '0.95rem'}}>{feature.desc}</p>
        </div>
      ))}
    </div>
  </div>
</section>

{/* Stats Section */}
<section style={{padding: '6rem 2rem', background: '#111111', color: '#ffffff'}}>
  <div style={{maxWidth: '1280px', margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '2rem', textAlign: 'center'}}>
    {[
      {value: '10k+', label: 'Users'},
      {value: '98%', label: 'Satisfaction'},
      {value: '500+', label: 'Projects Completed'},
      {value: '24/7', label: 'Support'}
    ].map((stat, index) => (
      <div key={index} style={{
        background: 'rgba(255,255,255,0.05)',
        borderRadius: '16px',
        padding: '2rem',
        border: '1px solid rgba(255,255,255,0.1)'
      }}>
        <div style={{
          fontSize: '2.5rem',
          fontWeight: 'bold',
          background: 'linear-gradient(135deg, #ffb917 0%, #206EB6 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>{stat.value}</div>
        <div style={{color: 'rgba(255,255,255,0.7)', marginTop: '0.5rem'}}>{stat.label}</div>
      </div>
    ))}
  </div>
</section>

{/* Pricing Section */}
<section id="pricing" style={{padding: '6rem 2rem', backgroundColor: '#000000', color: '#ffffff'}}>
  <div style={{maxWidth: '1280px', margin: '0 auto', textAlign: 'center', marginBottom: '4rem'}}>
    <h2 style={{fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '1rem', background: 'linear-gradient(135deg, #ffb917 0%, #206EB6 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'}}>
      Pricing Plans
    </h2>
    <p style={{color: 'rgba(255,255,255,0.7)', fontSize: '1.1rem'}}>
      Choose a plan that fits your needs. Simple, transparent pricing.
    </p>
  </div>
  <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem', maxWidth: '1280px', margin: '0 auto'}}>
    {[
      {title: 'Starter', price: '$29/mo', features: ['Basic Analytics', 'Up to 3 Dashboards', 'Email Support'], highlighted: false},
      {title: 'Pro', price: '$99/mo', features: ['Advanced Analytics', 'Unlimited Dashboards', 'Priority Support'], highlighted: true},
      {title: 'Enterprise', price: '$249/mo', features: ['Custom Solutions', 'Dedicated Manager', '24/7 Support'], highlighted: false}
    ].map((plan, index) => (
      <div key={index} style={{
        background: plan.highlighted ? 'linear-gradient(135deg, #ffb917 0%, #206EB6 100%)' : 'rgba(255,255,255,0.05)',
        color: plan.highlighted ? '#000000' : '#ffffff',
        borderRadius: '16px',
        padding: '2rem',
        border: plan.highlighted ? 'none' : '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        boxShadow: plan.highlighted ? '0 10px 30px rgba(255,185,23,0.3)' : '0 10px 30px rgba(0,0,0,0.3)'
      }}>
        <h3 style={{fontSize: '1.5rem', fontWeight: '600'}}>{plan.title}</h3>
        <div style={{fontSize: '2rem', fontWeight: 'bold'}}>{plan.price}</div>
        <ul style={{listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem'}}>
          {plan.features.map((feat, i) => (
            <li key={i} style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
              <Check size={16} color={plan.highlighted ? '#000000' : '#ffb917'} />
              {feat}
            </li>
          ))}
        </ul>
        <button style={{
          marginTop: '1rem',
          padding: '0.75rem',
          borderRadius: '12px',
          border: 'none',
          cursor: 'pointer',
          fontWeight: '600',
          background: plan.highlighted ? '#000000' : 'linear-gradient(135deg, #ffb917 0%, #206EB6 100%)',
          color: plan.highlighted ? '#ffb917' : '#ffffff',
          transition: 'all 0.3s ease'
        }}>
          Choose Plan
        </button>
      </div>
    ))}
  </div>
</section>


      <style jsx>{`
        @keyframes slideInLeft {
          from { opacity: 0; transform: translateX(-50px); }
          to { opacity: 1; transform: translateX(0); }
        }
        @keyframes slideInRight {
          from { opacity: 0; transform: translateX(50px); }
          to { opacity: 1; transform: translateX(0); }
        }
      `}</style>
    </div>
  );
};

export default VisionUILanding;
