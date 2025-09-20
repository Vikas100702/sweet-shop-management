/**
 * Main App component - Sweet Shop Management System
 */

import { useEffect, useState } from "react";
import "./App.css";
import apiService from "./services/api";

function App() {
  const [apiStatus, setApiStatus] = useState("Checking API status...");

  useEffect(() => {
    // Test API connection
    const testApi = async () => {
      try {
        // Try to fetch sweets (this will fail if not authenticated, but shows API is working)
        await apiService.getSweets();
        setApiStatus('API Connected (Authentication required)');
      } catch (error) {
        if (error.message.includes('401') || error.message.includes('Session expired')) {
          setApiStatus('API Connected (Ready for authentication)');
        } else {
          setApiStatus(`API Error: ${error.message}`);
        }
      }
    };
    testApi();    
  }, []);

  return (
    <div className="App">
      <header className = "App-header">
        <h1>Sweet Shop Management System</h1>
        <p>Welcome to our delicious world of sweets!</p>
        <div className="card" style={{marginTop: '2rem', padding: '1rem'}}>
          <h3>API Status</h3>
          <p>{apiStatus}</p>
          <small style={{color: 'rgba(255, 255, 255, 0.7)'}}>
            Backend: {process.env.REACT_APP_API_URL || 'http://localhost:8000'}
          </small>
        </div>
      </header>
    </div>
  )
}

export default App;