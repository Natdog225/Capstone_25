import React, { useState, useEffect } from 'react';
import {
  // Only keeping used recharts components
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import {
  ChevronRight, Zap, Shield, TrendingUp, Users, Activity,
  Layers, Award, ArrowUp, Menu, X, Star, Check
} from 'lucide-react';

const VisionUILanding = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [activeMetric, setActiveMetric] = useState(0);

  // Sample data for charts
  const lineData = [
    { name: 'Jan', value: 2400 },
    { name: 'Feb', value: 1398 },
    { name: 'Mar', value: 9800 },
    { name: 'Apr', value: 3908 },
    { name: 'May', value: 4800 },
    { name: 'Jun', value: 3800 },
    { name: 'Jul', value: 4300 }
  ];

  // Removed unused variable: radialData

  const metrics = [
    { value: '$53,000', label: 'Total Revenue', change: '+55%', icon: TrendingUp },
    { value: '2,300', label: 'Total Users', change: '+5%', icon: Users },
    { value: '3,052', label: 'New Orders', change: '+14%', icon: Activity },
    { value: '$173,000', label: 'Total Sales', change: '+8%', icon: Zap }
  ];

  // Fixed useEffect dependency warning by adding [metrics]
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveMetric((prev) => (prev + 1) % metrics.length);
    }, 3000);
    return () => clearInterval(interval);
  }, [metrics]);

  const styles = {
    container: {
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0B1929 0%, #111C44 50%, #0B1929 100%)',
      color: '#fff',
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
      background: 'rgba(11, 25, 41, 0.8)',
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
      background: 'linear-gradient(135deg, #00D9FF 0%, #7B42F6 100%)',
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
      background: 'linear-gradient(135deg, #fff 0%, #00D9FF 50%, #7B42F6 100%)',
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
      background: 'linear-gradient(135deg, #00D9FF 0%, #7B42F6 100%)',
      border: 'none',
      borderRadius: '12px',
      color: '#fff',
      fontSize: '1rem',
      fontWeight: '600',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      transition: 'all 0.3s ease',
      boxShadow: '0 4px 20px rgba(0, 217, 255, 0.3)'
    },
    secondaryButton: {
      padding: '0.75rem 2rem',
      background: 'rgba(255, 255, 255, 0.1)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      borderRadius: '12px',
      color: '#fff',
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
      background: 'linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(123, 66, 246, 0.1) 100%)',
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
    featuresSection: {
      padding: '80px 0',
      position: 'relative',
      zIndex: 10
    },
    sectionTitle: {
      textAlign: 'center',
      fontSize: '2.5rem',
      fontWeight: 'bold',
      marginBottom: '1rem',
      background: 'linear-gradient(135deg, #fff 0%, #00D9FF 100%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent'
    },
    sectionSubtitle: {
      textAlign: 'center',
      fontSize: '1.125rem',
      color: 'rgba(255, 255, 255, 0.7)',
      marginBottom: '3rem',
      maxWidth: '600px',
      margin: '0 auto 3rem'
    },
    featuresGrid: {
      maxWidth: '1280px',
      margin: '0 auto',
      padding: '0 2rem',
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
      gap: '2rem'
    },
    featureCard: {
      background: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '20px',
      padding: '2rem',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(20px)',
      transition: 'all 0.3s ease',
      cursor: 'pointer'
    },
    featureIcon: {
      width: '60px',
      height: '60px',
      background: 'linear-gradient(135deg, #00D9FF 0%, #7B42F6 100%)',
      borderRadius: '16px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      marginBottom: '1.5rem'
    },
    featureTitle: {
      fontSize: '1.25rem',
      fontWeight: '600',
      marginBottom: '1rem'
    },
    featureDescription: {
      color: 'rgba(255, 255, 255, 0.7)',
      lineHeight: 1.6
    },
    statsSection: {
      padding: '80px 0',
      background: 'rgba(0, 0, 0, 0.3)'
    },
    statsGrid: {
      maxWidth: '1280px',
      margin: '0 auto',
      padding: '0 2rem',
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
      gap: '2rem'
    },
    statCard: {
      textAlign: 'center',
      padding: '2rem',
      background: 'rgba(255, 255, 255, 0.03)',
      borderRadius: '20px',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(10px)'
    },
    statNumber: {
      fontSize: '3rem',
      fontWeight: 'bold',
      background: 'linear-gradient(135deg, #00D9FF 0%, #7B42F6 100%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent'
    },
    statLabel: {
      color: 'rgba(255, 255, 255, 0.7)',
      marginTop: '0.5rem'
    },
    pricingSection: {
      padding: '80px 0',
      position: 'relative',
      zIndex: 10
    },
    pricingGrid: {
      maxWidth: '1280px',
      margin: '0 auto',
      padding: '0 2rem',
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
      gap: '2rem'
    },
    pricingCard: {
      background: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '24px',
      padding: '2.5rem',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(20px)',
      position: 'relative',
      transition: 'all 0.3s ease'
    },
    pricingHighlight: {
      background: 'linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(123, 66, 246, 0.1) 100%)',
      border: '1px solid rgba(0, 217, 255, 0.3)',
      transform: 'scale(1.05)'
    },
    popularBadge: {
      position: 'absolute',
      top: '-12px',
      right: '24px',
      background: 'linear-gradient(135deg, #00D9FF 0%, #7B42F6 100%)',
      padding: '0.25rem 1rem',
      borderRadius: '20px',
      fontSize: '0.875rem',
      fontWeight: '600'
    },
    pricingPlan: {
      fontSize: '1.25rem',
      fontWeight: '600',
      marginBottom: '0.5rem'
    },
    pricingPrice: {
      fontSize: '3rem',
      fontWeight: 'bold',
      marginBottom: '0.5rem'
    },
    pricingPeriod: {
      color: 'rgba(255, 255, 255, 0.6)',
      marginBottom: '2rem'
    },
    pricingFeatures: {
      listStyle: 'none',
      padding: 0,
      marginBottom: '2rem'
    },
    pricingFeature: {
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
      marginBottom: '1rem',
      color: 'rgba(255, 255, 255, 0.8)'
    },
    footer: {
      padding: '40px 0',
      borderTop: '1px solid rgba(255, 255, 255, 0.1)',
      background: 'rgba(0, 0, 0, 0.3)'
    },
    footerContent: {
      maxWidth: '1280px',
      margin: '0 auto',
      padding: '0 2rem',
      textAlign: 'center',
      color: 'rgba(255, 255, 255, 0.6)'
    }
  };

  return (
    <div style={styles.container}>
      {/* Background Effects */}
      <div style={styles.backgroundEffects}>
        <div style={{...styles.glowOrb, width: '600px', height: '600px', top: '-200px', left: '-200px', background: 'radial-gradient(circle, #00D9FF 0%, transparent 70%)'}} />
        <div style={{...styles.glowOrb, width: '800px', height: '800px', bottom: '-300px', right: '-300px', background: 'radial-gradient(circle, #7B42F6 0%, transparent 70%)'}} />
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
            <button style={styles.primaryButton}>
              Get Started
            </button>
          </div>
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            style={{display: window.innerWidth <= 768 ? 'block' : 'none', background: 'none', border: 'none', color: '#fff', cursor: 'pointer'}}
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
                <Star size={20} style={{color: '#FFD700'}} />
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
                    <div style={{color: '#00D9FF'}}>
                      <metric.icon size={24} />
                    </div>
                  </div>
                  <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.5rem', color: '#00D9FF', fontSize: '0.875rem'}}>
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
                      <stop offset="5%" stopColor="#00D9FF" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#7B42F6" stopOpacity={0.2}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="name" stroke="rgba(255,255,255,0.5)" />
                  <YAxis stroke="rgba(255,255,255,0.5)" />
                  <Tooltip
                    contentStyle={{background: 'rgba(17, 28, 68, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px'}}
                    labelStyle={{color: '#fff'}}
                  />
                  <Line type="monotone" dataKey="value" stroke="#00D9FF" strokeWidth={3} fill="url(#colorGradient)" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" style={styles.featuresSection}>
        <h2 style={styles.sectionTitle}>Powerful Features</h2>
        <p style={styles.sectionSubtitle}>
          Everything you need to build stunning dashboards and admin panels
        </p>
        <div style={styles.featuresGrid}>
          <div style={styles.featureCard} onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-10px)'} onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}>
            <div style={styles.featureIcon}>
              <Zap size={30} color="#fff" />
            </div>
            <h3 style={styles.featureTitle}>Lightning Fast</h3>
            <p style={styles.featureDescription}>
              Optimized performance with lazy loading and code splitting for instant page loads.
            </p>
          </div>
          <div style={styles.featureCard} onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-10px)'} onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}>
            <div style={styles.featureIcon}>
              <Shield size={30} color="#fff" />
            </div>
            <h3 style={styles.featureTitle}>Secure by Default</h3>
            <p style={styles.featureDescription}>
              Built-in authentication, role-based access control, and data encryption.
            </p>
          </div>
          <div style={styles.featureCard} onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-10px)'} onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}>
            <div style={styles.featureIcon}>
              <Layers size={30} color="#fff" />
            </div>
            <h3 style={styles.featureTitle}>Modular Design</h3>
            <p style={styles.featureDescription}>
              Component-based architecture makes it easy to customize and extend.
            </p>
          </div>
          <div style={styles.featureCard} onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-10px)'} onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}>
            <div style={styles.featureIcon}>
              <Activity size={30} color="#fff" />
            </div>
            <h3 style={styles.featureTitle}>Real-time Analytics</h3>
            <p style={styles.featureDescription}>
              Live data visualization with interactive charts and customizable widgets.
            </p>
          </div>
          <div style={styles.featureCard} onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-10px)'} onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}>
            <div style={styles.featureIcon}>
              <Users size={30} color="#fff" />
            </div>
            <h3 style={styles.featureTitle}>Team Collaboration</h3>
            <p style={styles.featureDescription}>
              Built-in tools for team communication, task management, and file sharing.
            </p>
          </div>
          <div style={styles.featureCard} onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-10px)'} onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}>
            <div style={styles.featureIcon}>
              <TrendingUp size={30} color="#fff" />
            </div>
            <h3 style={styles.featureTitle}>Growth Focused</h3>
            <p style={styles.featureDescription}>
              Track KPIs, set goals, and monitor progress with advanced reporting tools.
            </p>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section style={styles.statsSection}>
        <div style={styles.statsGrid}>
          <div style={styles.statCard}>
            <div style={styles.statNumber}>50K+</div>
            <div style={styles.statLabel}>Active Users</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statNumber}>99.9%</div>
            <div style={styles.statLabel}>Uptime</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statNumber}>150+</div>
            <div style={styles.statLabel}>Components</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statNumber}>24/7</div>
            <div style={styles.statLabel}>Support</div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" style={styles.pricingSection}>
        <h2 style={styles.sectionTitle}>Simple, Transparent Pricing</h2>
        <p style={styles.sectionSubtitle}>
          Choose the perfect plan for your needs. Always flexible to scale
        </p>
        <div style={styles.pricingGrid}>
          <div style={styles.pricingCard}>
            <div style={styles.pricingPlan}>Starter</div>
            <div style={styles.pricingPrice}>$29</div>
            <div style={styles.pricingPeriod}>per month</div>
            <ul style={styles.pricingFeatures}>
              <li style={styles.pricingFeature}>
                <Check size={20} style={{color: '#00D9FF'}} />
                Up to 10 users
              </li>
              <li style={styles.pricingFeature}>
                <Check size={20} style={{color: '#00D9FF'}} />
                20 projects
              </li>
              <li style={styles.pricingFeature}>
                <Check size={20} style={{color: '#00D9FF'}} />
                Basic analytics
              </li>
              <li style={styles.pricingFeature}>
                <Check size={20} style={{color: '#00D9FF'}} />
                24/7 support
              </li>
            </ul>
            <button style={{...styles.secondaryButton, width: '100%'}}>
              Start Free Trial
            </button>
          </div>
          <div style={{...styles.pricingCard, ...styles.pricingHighlight}}>
            <div style={styles.popularBadge}>Most Popular</div>
            <div style={styles.pricingPlan}>Professional</div>
            <div style={styles.pricingPrice}>$99</div>
            <div style={styles.pricingPeriod}>per month</div>
            <ul style={styles.pricingFeatures}>
              <li style={styles.pricingFeature}>
                <Check size={20} style={{color: '#00D9FF'}} />
                Unlimited users
              </li>
              <li style={styles.pricingFeature}>
                <Check size={20} style={{color: '#00D9FF'}} />
                Unlimited projects
              </li>
              <li style={styles.pricingFeature}>
                <Check size={20} style={{color: '#00D9FF'}} />
                Advanced analytics
              </li>
              <li style={styles.pricingFeature}>
                <Check size={20} style={{color: '#00D9FF'}} />
                Priority support
              </li>
              <li style={styles.pricingFeature}>
                <Check size={20} style={{color: '#00D9FF'}} />
                Custom integrations
              </li>
            </ul>
            <button style={{...styles.primaryButton, width: '100%'}}>
              Start Free Trial
            </button>
          </div>
          <div style={styles.pricingCard}>
            <div style={styles.pricingPlan}>Enterprise</div>
            <div style={styles.pricingPrice}>Custom</div>
            <div style={styles.pricingPeriod}>contact sales</div>
            <ul style={styles.pricingFeatures}>
              <li style={styles.pricingFeature}>
                <Check size={20} style={{color: '#00D9FF'}} />
                Everything in Pro
              </li>
              <li style={styles.pricingFeature}>
                <Check size={20} style={{color: '#00D9FF'}} />
                SSO & SAML
              </li>
              <li style={styles.pricingFeature}>
                <Check size={20} style={{color: '#00D9FF'}} />
                Custom contracts
              </li>
              <li style={styles.pricingFeature}>
                <Check size={20} style={{color: '#00D9FF'}} />
                Dedicated manager
              </li>
            </ul>
            <button style={{...styles.secondaryButton, width: '100%'}}>
              Contact Sales
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={styles.footer}>
        <div style={styles.footerContent}>
          <div style={{...styles.logo, justifyContent: 'center', marginBottom: '1rem'}}>
            <Layers size={28} />
            Vision UI
          </div>
          <p>© 2024 Vision UI Dashboard. Crafted with passion for the future.</p>
        </div>
      </footer>

      {/* Add CSS animations */}
      <style jsx>{`
        @keyframes slideInLeft {
          from {
            opacity: 0;
            transform: translateX(-50px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        
        @keyframes slideInRight {
          from {
            opacity: 0;
            transform: translateX(50px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
      `}</style>
    </div>
  );
};

export default VisionUILanding;