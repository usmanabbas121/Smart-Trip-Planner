import React, { useState, useEffect, useRef } from 'react';
import TripForm from './components/TripForm';
import MapDisplay from './components/MapDisplay';
import LogSheets from './components/LogSheets';
import { TripResponse } from './types';
import { FaRoute, FaExclamationTriangle, FaCheckCircle, FaExclamationCircle, FaRuler, FaClock, FaShieldAlt } from 'react-icons/fa';
import './App.css';

function App() {
  const [tripData, setTripData] = useState<TripResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  const handleTripCalculated = (data: TripResponse) => {
    setTripData(data);
    setError(null);
  };

  useEffect(() => {
    if (tripData && resultsRef.current) {
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'start' 
        });
      }, 100);
    }
  }, [tripData]);

  const handleError = (err: string) => {
    setError(err);
    setTripData(null);
  };

  const handleLoading = (isLoading: boolean) => {
    setLoading(isLoading);
  };

  const handleNewTrip = () => {
    setTripData(null);
    setError(null);
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-left-content">
          <img src="/icons/logo.png" alt="Logo" className="header-logo" />
          <h1>
            Smart Trip Planner
          </h1>
        </div>
        <div className="header-footer-text">
          <div className="header-powered-by">
            powered by : <span className="spotter-link">spotter.ai</span>
          </div>
          <div className="header-developed-by">
            developed by : <span className="developer-name">Usman Abbas</span>
          </div>
        </div>
      </header>
      <main className="App-main">
        {tripData && (
          <div style={{ marginBottom: '20px', textAlign: 'right' }}>
            <button 
              onClick={handleNewTrip}
              className="new-trip-button"
            >
              <FaRoute style={{ marginRight: '8px', color: '#ffffff' }} />
              Calculate New Trip
            </button>
          </div>
        )}
        <TripForm
          onTripCalculated={handleTripCalculated}
          onError={handleError}
          onLoading={handleLoading}
          resetTrigger={tripData === null}
        />
        {error && (
          <div className="error">
            <FaExclamationTriangle style={{ marginRight: '8px', color: '#ffffff' }} />
            {error}
          </div>
        )}
        {tripData && (
          <div ref={resultsRef}>
            <MapDisplay route={tripData.route} timeline={tripData.timeline} />
            <div className="summary">
              <h2>
                <FaRoute style={{ marginRight: '8px', verticalAlign: 'middle', color: '#c31432' }} />
                Trip Summary
              </h2>
              <p>
                <FaRuler style={{ marginRight: '8px', color: '#c31432' }} />
                Total Distance: {tripData.route.distance_miles.toFixed(2)} miles
              </p>
              <p>
                <FaClock style={{ marginRight: '8px', color: '#c31432' }} />
                Total Driving Hours: {tripData.summary.total_driving_hours.toFixed(2)}
              </p>
              <p>
                <FaClock style={{ marginRight: '8px', color: '#c31432' }} />
                Total On-Duty Hours: {tripData.summary.total_on_duty_hours.toFixed(2)}
              </p>
              <p>
                <FaShieldAlt style={{ marginRight: '8px', color: tripData.compliance.compliant ? '#4CAF50' : '#c31432' }} />
                Compliance: {tripData.compliance.compliant ? (
                  <span style={{ 
                    color: '#4CAF50', 
                    fontWeight: '600',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}>
                    <FaCheckCircle style={{ verticalAlign: 'middle' }} /> Compliant
                  </span>
                ) : (
                  <span style={{ 
                    color: '#c31432', 
                    fontWeight: '500',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '2px',
                    padding: '1px 4px 1px 8px',
                    backgroundColor: 'rgba(195, 20, 50, 0.1)',
                    borderRadius: '3px',
                    border: '1px solid rgba(195, 20, 50, 0.2)',
                    fontSize: '0.75rem',
                    marginLeft: '8px'
                  }}>
                    <FaExclamationCircle style={{ verticalAlign: 'middle', fontSize: '0.7rem' }} /> Non-Compliant
                  </span>
                )}
              </p>
              {!tripData.compliance.compliant && (
                <p className="error">
                  <FaExclamationTriangle style={{ marginRight: '8px', color: '#ffffff' }} />
                  Exceeds 70-hour limit by {tripData.compliance.exceeds_by.toFixed(2)} hours
                </p>
              )}
            </div>
            <LogSheets logSheets={tripData.log_sheets} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;

