/**
 * Simple toast notification system
 * Shows success, error, and info messages to users
 */
import React, { useState, useEffect } from 'react';

// Toast management
let toastId = 0;
const toastListeners = [];

/**
 * Show a toast notification
 * @param {string} message - Message to display
 * @param {string} type - Toast type (success, error, info)
 * @returns {number} Toast ID for potential removal
 */
export const showToast = (message, type = 'info') => {
  const toast = {
    id: ++toastId,
    message,
    type,
    timestamp: Date.now(),
  };
  
  // Notify all listeners
  toastListeners.forEach(listener => listener(toast));
  
  return toast.id;
};

/**
 * Toast component to display notifications
 */
export const Toast = () => {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    // Register listener for new toasts
    const listener = (toast) => {
      setToasts(prev => [...prev, toast]);
      
      // Auto remove after 4 seconds
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== toast.id));
      }, 4000);
    };
    
    toastListeners.push(listener);
    
    // Cleanup listener on unmount
    return () => {
      const index = toastListeners.indexOf(listener);
      if (index > -1) {
        toastListeners.splice(index, 1);
      }
    };
  }, []);

  /**
   * Remove a specific toast
   * @param {number} id - Toast ID to remove
   */
  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  if (toasts.length === 0) return null;

  return (
    <div style={toastContainerStyle}>
      {toasts.map(toast => (
        <div
          key={toast.id}
          className={`toast toast-${toast.type}`}
          style={getToastStyle(toast.type)}
          onClick={() => removeToast(toast.id)}
        >
          {getToastIcon(toast.type)} {toast.message}
          <span style={{ marginLeft: '10px', opacity: 0.7, cursor: 'pointer' }}>×</span>
        </div>
      ))}
    </div>
  );
};

// Toast container styles
const toastContainerStyle = {
  position: 'fixed',
  top: '20px',
  right: '20px',
  zIndex: 1100,
  maxWidth: '400px'
};

// Get toast styles based on type
const getToastStyle = (type) => ({
  padding: '16px 20px',
  marginBottom: '10px',
  borderRadius: '8px',
  color: 'white',
  fontWeight: '500',
  cursor: 'pointer',
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  animation: 'slideIn 0.3s ease-out',
  background: getToastBackground(type),
  border: `1px solid ${getToastBorderColor(type)}`,
});

// Get background color based on toast type
const getToastBackground = (type) => {
  switch (type) {
    case 'success':
      return 'linear-gradient(45deg, #10b981, #059669)';
    case 'error':
      return 'linear-gradient(45deg, #ef4444, #dc2626)';
    case 'info':
    default:
      return 'linear-gradient(45deg, #3b82f6, #2563eb)';
  }
};

// Get border color based on toast type
const getToastBorderColor = (type) => {
  switch (type) {
    case 'success':
      return 'rgba(16, 185, 129, 0.3)';
    case 'error':
      return 'rgba(239, 68, 68, 0.3)';
    case 'info':
    default:
      return 'rgba(59, 130, 246, 0.3)';
  }
};

// Get icon based on toast type
const getToastIcon = (type) => {
  switch (type) {
    case 'success':
      return '✅';
    case 'error':
      return '❌';
    case 'info':
    default:
      return 'ℹ️';
  }
};

// Helper functions for different toast types
export const showSuccess = (message) => showToast(message, 'success');
export const showError = (message) => showToast(message, 'error');
export const showInfo = (message) => showToast(message, 'info');

// Add CSS animation to global styles