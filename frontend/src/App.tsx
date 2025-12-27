import React, { useState, useEffect, useRef } from 'react';
import TripForm from './components/TripForm';
import MapDisplay from './components/MapDisplay';
import LogSheets from './components/LogSheets';
import { TripResponse } from './types';
import { FaRoute, FaExclamationTriangle, FaCheckCircle, FaExclamationCircle, FaRuler, FaClock, FaShieldAlt, FaGasPump, FaBed } from 'react-icons/fa';
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
        {error && !loading && (
          <div className="error">
            <FaExclamationTriangle style={{ marginRight: '8px', color: '#ffffff' }} />
            {error}
          </div>
        )}
        {tripData && (
          <div ref={resultsRef}>
            <MapDisplay route={tripData.route} timeline={tripData.timeline} />
            <div className="summary-modern">
              <div className="summary-header">
                <FaRoute className="summary-header-icon" />
                <span>Trip Summary</span>
              </div>
              <div className="summary-cards">
                <div className="summary-card">
                  <div className="card-icon distance">
                    <FaRuler />
                  </div>
                  <div className="card-content">
                    <span className="card-label">Total Distance</span>
                    <span className="card-value">{tripData.route.distance_miles.toFixed(2)} <small>miles</small></span>
                  </div>
                </div>
                <div className="summary-card">
                  <div className="card-icon driving">
                    <FaClock />
                  </div>
                  <div className="card-content">
                    <span className="card-label">Driving Hours</span>
                    <span className="card-value">{tripData.summary.total_driving_hours.toFixed(2)} <small>hrs</small></span>
                  </div>
                </div>
                <div className="summary-card">
                  <div className="card-icon onduty">
                    <FaClock />
                  </div>
                  <div className="card-content">
                    <span className="card-label">On-Duty Hours</span>
                    <span className="card-value">{tripData.summary.total_on_duty_hours.toFixed(2)} <small>hrs</small></span>
                  </div>
                </div>
                <div className="summary-card">
                  <div className="card-icon fuel">
                    <FaGasPump />
                  </div>
                  <div className="card-content">
                    <span className="card-label">Fuel Stops</span>
                    <span className="card-value">{tripData.route.fuel_stops.length}</span>
                  </div>
                </div>
                <div className="summary-card">
                  <div className="card-icon rest">
                    <FaBed />
                  </div>
                  <div className="card-content">
                    <span className="card-label">Rest Breaks</span>
                    <span className="card-value">{tripData.timeline.filter(e => e.status === 'sleeper_berth').length}</span>
                  </div>
                </div>
                <div className={`summary-card compliance ${tripData.compliance.compliant ? 'compliant' : 'non-compliant'}`}>
                  <div className={`card-icon ${tripData.compliance.compliant ? 'compliant' : 'non-compliant'}`}>
                    <FaShieldAlt />
                  </div>
                  <div className="card-content">
                    <span className="card-label">Compliance</span>
                    <span className="card-value status">
                      {tripData.compliance.compliant ? (
                        <><FaCheckCircle /> Compliant</>
                      ) : (
                        <><FaExclamationCircle /> Non-Compliant</>
                      )}
                    </span>
                  </div>
                </div>
              </div>
              {!tripData.compliance.compliant && (
                <div className="compliance-warning">
                  <FaExclamationTriangle />
                  <span>Exceeds 70-hour limit by {tripData.compliance.exceeds_by.toFixed(2)} hours</span>
                </div>
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

