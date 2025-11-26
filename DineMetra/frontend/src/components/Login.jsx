import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  signInWithPopup 
} from 'firebase/auth';
import { auth, googleProvider } from '../firebase';
import './Login.css'; // Import the CSS file

const DineMetraAuth = () => {
  const navigate = useNavigate();
  const [isSignUp, setIsSignUp] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSignIn = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await signInWithEmailAndPassword(auth, formData.email, formData.password);
      navigate('/dashboard');
    } catch (error) {
      setError(error.message.replace('Firebase: ', ''));
    } finally {
      setLoading(false);
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    setError('');
    
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match!');
      return;
    }
    
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    try {
      await createUserWithEmailAndPassword(auth, formData.email, formData.password);
      navigate('/dashboard');
    } catch (error) {
      setError(error.message.replace('Firebase: ', ''));
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setError('');
    setLoading(true);
    try {
      await signInWithPopup(auth, googleProvider);
      navigate('/dashboard');
    } catch (error) {
      setError(error.message.replace('Firebase: ', ''));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: '#206eb6',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      padding: '1rem'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '400px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 'clamp(1rem, 3vw, 2rem)'
      }}>
        {/* Logo with Dinner Plate */}
        <div style={{
          textAlign: 'center',
          marginBottom: '0.5rem',
          width: '100%'
        }}>
          <div className="dinner-plate-logo">
            <div className="dinner-plate">
              <img 
                src="/DineMetra_Logo.png"
                alt="DineMetra Logo" 
              />
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div style={{
            width: '100%',
            padding: '1rem',
            background: '#ff4444',
            color: '#fff',
            borderRadius: '8px',
            textAlign: 'center',
            fontSize: '0.9rem'
          }}>
            {error}
          </div>
        )}

        {!isSignUp ? (
          // Sign In Form
          <>
            <div style={{
              background: '#ffffff',
              borderRadius: '8px',
              padding: 'clamp(1.5rem, 4vw, 2rem)',
              width: '100%',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)'
            }}>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: 'clamp(1rem, 3vw, 1.5rem)'
              }}>
                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '0.5rem',
                    color: '#1E1E1E',
                    fontSize: '0.95rem',
                    fontWeight: '500'
                  }}>
                    Email
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="Enter your email"
                    required
                    disabled={loading}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontSize: '1rem',
                      boxSizing: 'border-box',
                      outline: 'none',
                      transition: 'border-color 0.3s',
                      opacity: loading ? 0.6 : 1
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#206eb6'}
                    onBlur={(e) => e.target.style.borderColor = '#ddd'}
                  />
                </div>

                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '0.5rem',
                    color: '#1E1E1E',
                    fontSize: '0.95rem',
                    fontWeight: '500'
                  }}>
                    Password
                  </label>
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    placeholder="Enter your password"
                    required
                    disabled={loading}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontSize: '1rem',
                      boxSizing: 'border-box',
                      outline: 'none',
                      transition: 'border-color 0.3s',
                      opacity: loading ? 0.6 : 1
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#206eb6'}
                    onBlur={(e) => e.target.style.borderColor = '#ddd'}
                  />
                </div>

                <button
                  onClick={handleSignIn}
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '0.875rem',
                    background: loading ? '#666' : '#1E1E1E',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '4px',
                    fontSize: '1rem',
                    fontWeight: '600',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    transition: 'background 0.3s'
                  }}
                  onMouseEnter={(e) => !loading && (e.target.style.background = '#2d2d2d')}
                  onMouseLeave={(e) => !loading && (e.target.style.background = '#1E1E1E')}
                >
                  {loading ? 'Signing In...' : 'Sign In'}
                </button>

                {/* Google Sign In Button */}
                <button
                  onClick={handleGoogleSignIn}
                  type="button"
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '0.875rem',
                    background: '#ffffff',
                    color: '#1E1E1E',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '1rem',
                    fontWeight: '600',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    transition: 'all 0.3s',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.5rem',
                    opacity: loading ? 0.6 : 1
                  }}
                  onMouseEnter={(e) => {
                    if (!loading) {
                      e.target.style.background = '#f5f5f5';
                      e.target.style.borderColor = '#206eb6';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!loading) {
                      e.target.style.background = '#ffffff';
                      e.target.style.borderColor = '#ddd';
                    }
                  }}
                >
                  <svg width="18" height="18" viewBox="0 0 18 18">
                    <path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.875 2.684-6.615z"/>
                    <path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332C2.438 15.983 5.482 18 9 18z"/>
                    <path fill="#FBBC05" d="M3.964 10.707c-.18-.54-.282-1.117-.282-1.707 0-.593.102-1.17.282-1.709V4.958H.957C.347 6.173 0 7.548 0 9s.348 2.827.957 4.042l3.007-2.335z"/>
                    <path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0 5.482 0 2.438 2.017.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z"/>
                  </svg>
                  {loading ? 'Signing In...' : 'Sign in with Google'}
                </button>
              </div>
            </div>

            <div style={{
              color: '#ffffff',
              fontSize: '1.25rem',
              fontWeight: '300'
            }}>
              or
            </div>

            <button
              onClick={() => setIsSignUp(true)}
              disabled={loading}
              style={{
                width: '100%',
                maxWidth: '250px',
                padding: '0.875rem',
                background: loading ? '#666' : '#1E1E1E',
                color: '#ffffff',
                border: 'none',
                borderRadius: '4px',
                fontSize: '1rem',
                fontWeight: '600',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'background 0.3s'
              }}
              onMouseEnter={(e) => !loading && (e.target.style.background = '#2d2d2d')}
              onMouseLeave={(e) => !loading && (e.target.style.background = '#1E1E1E')}
            >
              Sign Up
            </button>
          </>
        ) : (
          // Sign Up Form
          <>
            <div style={{
              background: '#ffffff',
              borderRadius: '8px',
              padding: 'clamp(1.5rem, 4vw, 2rem)',
              width: '100%',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)'
            }}>
              <h2 style={{
                color: '#1E1E1E',
                fontSize: 'clamp(1.5rem, 4vw, 2rem)',
                fontWeight: '600',
                textAlign: 'center',
                marginBottom: 'clamp(1.5rem, 3vw, 2rem)',
                letterSpacing: '0px'
              }}>
                Sign Up
              </h2>

              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: 'clamp(1rem, 3vw, 1.5rem)'
              }}>
                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '0.5rem',
                    color: '#1E1E1E',
                    fontSize: '0.95rem',
                    fontWeight: '500'
                  }}>
                    Email
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="Enter your email"
                    required
                    disabled={loading}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontSize: '1rem',
                      boxSizing: 'border-box',
                      outline: 'none',
                      transition: 'border-color 0.3s',
                      opacity: loading ? 0.6 : 1
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#206eb6'}
                    onBlur={(e) => e.target.style.borderColor = '#ddd'}
                  />
                </div>

                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '0.5rem',
                    color: '#1E1E1E',
                    fontSize: '0.95rem',
                    fontWeight: '500'
                  }}>
                    Password
                  </label>
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    placeholder="At least 6 characters"
                    required
                    disabled={loading}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontSize: '1rem',
                      boxSizing: 'border-box',
                      outline: 'none',
                      transition: 'border-color 0.3s',
                      opacity: loading ? 0.6 : 1
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#206eb6'}
                    onBlur={(e) => e.target.style.borderColor = '#ddd'}
                  />
                </div>

                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '0.5rem',
                    color: '#1E1E1E',
                    fontSize: '0.95rem',
                    fontWeight: '500'
                  }}>
                    Confirm Password
                  </label>
                  <input
                    type="password"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    placeholder="Re-enter password"
                    required
                    disabled={loading}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontSize: '1rem',
                      boxSizing: 'border-box',
                      outline: 'none',
                      transition: 'border-color 0.3s',
                      opacity: loading ? 0.6 : 1
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#206eb6'}
                    onBlur={(e) => e.target.style.borderColor = '#ddd'}
                  />
                </div>

                <button
                  onClick={handleSignUp}
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '0.875rem',
                    background: loading ? '#666' : '#1E1E1E',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '4px',
                    fontSize: '1rem',
                    fontWeight: '600',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    marginTop: '1rem',
                    transition: 'background 0.3s'
                  }}
                  onMouseEnter={(e) => !loading && (e.target.style.background = '#2d2d2d')}
                  onMouseLeave={(e) => !loading && (e.target.style.background = '#1E1E1E')}
                >
                  {loading ? 'Creating Account...' : 'Create Account'}
                </button>

                <button
                  type="button"
                  onClick={() => setIsSignUp(false)}
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    background: 'transparent',
                    color: '#1E1E1E',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '0.9rem',
                    fontWeight: '500',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    transition: 'all 0.3s',
                    opacity: loading ? 0.6 : 1
                  }}
                  onMouseEnter={(e) => {
                    if (!loading) {
                      e.target.style.background = '#f5f5f5';
                      e.target.style.borderColor = '#206eb6';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!loading) {
                      e.target.style.background = 'transparent';
                      e.target.style.borderColor = '#ddd';
                    }
                  }}
                >
                  Back to Sign In
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default DineMetraAuth;