/**
 * Login page component
 * Handles user authentication with form validation
 */
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { showSuccess, showError } from '../components/Toast';

const LoginPage = () => {
  const { login, user, loading } = useAuth();
  
  // Form state
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  
  // UI state
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState({});

  // Redirect if already authenticated
  useEffect(() => {
    if (user && !loading) {
      window.location.href = '/dashboard';
    }
  }, [user, loading]);

  /**
   * Validate login form
   * @returns {boolean} True if form is valid
   */
  const validateForm = () => {
    const newErrors = {};

    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Handle form submission
   * @param {Event} e - Form submit event
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    const result = await login(formData);
    
    if (result.success) {
      showSuccess(result.message);
      // Redirect will happen via useEffect
    } else {
      showError(result.message);
    }
    
    setIsSubmitting(false);
  };

  /**
   * Handle input changes and clear errors
   * @param {Event} e - Input change event
   */
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  // Show loading spinner while checking auth
  if (loading) {
    return (
      <div className="container" style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh' 
      }}>
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="container" style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '100vh',
      padding: '20px'
    }}>
      <div className="card" style={{ width: '100%', maxWidth: '400px' }}>
        {/* Header */}
        <div className="text-center mb-4">
          <div style={{
            width: '80px',
            height: '80px',
            background: 'linear-gradient(45deg, #ff6b6b, #4ecdc4)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1rem',
            fontSize: '2rem'
          }}>
            🍭
          </div>
          <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Welcome Back</h1>
          <p style={{ color: 'rgba(255, 255, 255, 0.8)' }}>
            Sign in to your Sweet Shop account
          </p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit}>
          {/* Username Field */}
          <div className="form-group">
            <label className="form-label">Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              disabled={isSubmitting}
              className={`form-input ${errors.username ? 'error' : ''}`}
              placeholder="Enter your username"
              autoComplete="username"
            />
            {errors.username && (
              <div className="form-error">{errors.username}</div>
            )}
          </div>

          {/* Password Field */}
          <div className="form-group">
            <label className="form-label">Password</label>
            <div style={{ position: 'relative' }}>
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                disabled={isSubmitting}
                className={`form-input ${errors.password ? 'error' : ''}`}
                placeholder="Enter your password"
                autoComplete="current-password"
                style={{ paddingRight: '50px' }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '15px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: 'rgba(255, 255, 255, 0.6)',
                  cursor: 'pointer',
                  fontSize: '1.1rem'
                }}
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
            {errors.password && (
              <div className="form-error">{errors.password}</div>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="btn btn-primary"
            style={{ width: '100%', padding: '12px' }}
          >
            {isSubmitting ? (
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                gap: '10px' 
              }}>
                <div className="loading-spinner" style={{ 
                  width: '20px', 
                  height: '20px',
                  border: '2px solid rgba(255,255,255,0.3)',
                  borderTop: '2px solid white'
                }}></div>
                Signing In...
              </div>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        {/* Demo Accounts Info */}
        <div style={{
          marginTop: '2rem',
          padding: '1rem',
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '8px',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        }}>
          <h4 style={{ 
            color: 'rgba(255, 255, 255, 0.9)', 
            fontSize: '0.9rem', 
            marginBottom: '0.5rem' 
          }}>
            Demo Accounts:
          </h4>
          <div style={{ fontSize: '0.8rem' }}>
            <div style={{ color: 'rgba(255, 255, 255, 0.7)', marginBottom: '0.25rem' }}>
              👤 User: <strong>testuser</strong> / <strong>test123</strong>
            </div>
            <div style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              🔧 Admin: <strong>admin</strong> / <strong>admin123</strong>
            </div>
          </div>
        </div>

        {/* Register Link */}
        <div className="text-center mt-4">
          <p style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '0.9rem' }}>
            Don't have an account?{' '}
            <button
              type="button"
              onClick={() => window.location.href = '/register'}
              style={{
                background: 'none',
                border: 'none',
                color: '#a5b4fc',
                textDecoration: 'underline',
                cursor: 'pointer',
                fontWeight: '500'
              }}
            >
              Sign up here
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;