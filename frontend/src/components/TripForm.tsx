import React, { useState, useEffect } from 'react';
import { calculateTrip } from '../services/api';
import { TripRequest, TripResponse } from '../types';
import { 
  FaRoute, 
  FaMapMarkerAlt, 
  FaClock, 
  FaBuilding, 
  FaUser, 
  FaTruck, 
  FaBox,
  FaFileAlt,
  FaSpinner
} from 'react-icons/fa';
import { HiOutlineClipboardDocumentList } from 'react-icons/hi2';
import './TripForm.css';

interface TripFormProps {
  onTripCalculated: (data: TripResponse) => void;
  onError: (error: string) => void;
  onLoading: (loading: boolean) => void;
  resetTrigger?: boolean;
}

const initialFormData: TripRequest = {
  current_location: '',
  pickup_location: '',
  dropoff_location: '',
  current_cycle_used: 0,
  carrier_name: '',
  main_office_address: '',
  home_terminal_address: '',
  driver_name: '',
  co_driver_name: '',
  truck_tractor: '',
  trailer: '',
  dvl_manifest_no: '',
  shipper_commodity: '',
  timezone: 'UTC'
};

const TripForm: React.FC<TripFormProps> = ({ onTripCalculated, onError, onLoading, resetTrigger }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<TripRequest>(initialFormData);

  useEffect(() => {
    if (resetTrigger) {
      setFormData({ ...initialFormData });
    }
  }, [resetTrigger]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'current_cycle_used' ? parseFloat(value) || 0 : value
    }));
  };

  const fillSampleData = () => {
    setFormData({
      current_location: 'Chicago, Illinois, USA',
      pickup_location: 'Indianapolis, Indiana, USA',
      dropoff_location: 'New York, New York, USA',
      current_cycle_used: 15.5,
      carrier_name: 'ABC Trucking Company',
      main_office_address: '123 Main St, Chicago, IL 60601',
      home_terminal_address: '456 Terminal Blvd, Chicago, IL 60601',
      driver_name: 'Usman Abbas',
      co_driver_name: 'John Doe',
      truck_tractor: 'TRK-12345',
      trailer: 'TRL-67890',
      dvl_manifest_no: 'DVL-2024-001234',
      shipper_commodity: 'General Freight - Electronics',
      timezone: 'America/Chicago'
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    onLoading(true);
    
    try {
      const response = await calculateTrip(formData);
      onTripCalculated(response);
    } catch (err: any) {
      const errorMessage = err?.message || err?.response?.data?.error || 'Failed to calculate trip. Please check your inputs and try again.';
      onError(errorMessage);
    } finally {
      setIsLoading(false);
      onLoading(false);
    }
  };

  return (
    <form className="trip-form" onSubmit={handleSubmit}>
      {!isLoading && resetTrigger && (
        <div style={{ marginBottom: '20px', textAlign: 'right' }}>
          <button 
            type="button" 
            onClick={fillSampleData}
            className="sample-data-button"
          >
            <HiOutlineClipboardDocumentList style={{ color: '#ffffff' }} />
            Fill Sample Data
          </button>
        </div>
      )}
      <div className="form-section">
        <h2>
          <FaRoute style={{ marginRight: '8px', verticalAlign: 'middle', color: '#c31432' }} />
          Trip Details
        </h2>
        <div className="form-group">
          <label>
            <FaMapMarkerAlt style={{ marginRight: '6px', color: '#c31432' }} />
            Current Location *
          </label>
          <input
            type="text"
            name="current_location"
            value={formData.current_location}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>
            <FaMapMarkerAlt style={{ marginRight: '6px', color: '#4CAF50' }} />
            Pickup Location *
          </label>
          <input
            type="text"
            name="pickup_location"
            value={formData.pickup_location}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>
            <FaMapMarkerAlt style={{ marginRight: '6px', color: '#f44336' }} />
            Dropoff Location *
          </label>
          <input
            type="text"
            name="dropoff_location"
            value={formData.dropoff_location}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>
            <FaClock style={{ marginRight: '6px', color: '#c31432' }} />
            Current Cycle Used (Hours) *
          </label>
          <input
            type="number"
            name="current_cycle_used"
            value={formData.current_cycle_used}
            onChange={handleChange}
            min="0"
            max="70"
            step="0.1"
            required
          />
        </div>
      </div>

      <div className="form-section">
        <h2>
          <FaBuilding style={{ marginRight: '8px', verticalAlign: 'middle', color: '#c31432' }} />
          Carrier Information (Optional)
        </h2>
        <div className="form-group">
          <label>
            <FaBuilding style={{ marginRight: '6px', color: '#c31432' }} />
            Carrier Name
          </label>
          <input
            type="text"
            name="carrier_name"
            value={formData.carrier_name}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>
            <FaMapMarkerAlt style={{ marginRight: '6px', color: '#c31432' }} />
            Main Office Address
          </label>
          <input
            type="text"
            name="main_office_address"
            value={formData.main_office_address}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>
            <FaMapMarkerAlt style={{ marginRight: '6px', color: '#c31432' }} />
            Home Terminal Address
          </label>
          <input
            type="text"
            name="home_terminal_address"
            value={formData.home_terminal_address}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>
            <FaUser style={{ marginRight: '6px', color: '#c31432' }} />
            Driver Name
          </label>
          <input
            type="text"
            name="driver_name"
            value={formData.driver_name}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>
            <FaUser style={{ marginRight: '6px', color: '#c31432' }} />
            Co-Driver Name
          </label>
          <input
            type="text"
            name="co_driver_name"
            value={formData.co_driver_name}
            onChange={handleChange}
          />
        </div>
      </div>

      <div className="form-section">
        <h2>
          <FaTruck style={{ marginRight: '8px', verticalAlign: 'middle', color: '#c31432' }} />
          Vehicle Information (Optional)
        </h2>
        <div className="form-group">
          <label>
            <FaTruck style={{ marginRight: '6px', color: '#c31432' }} />
            Truck/Tractor Number
          </label>
          <input
            type="text"
            name="truck_tractor"
            value={formData.truck_tractor}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>
            <FaBox style={{ marginRight: '6px', color: '#c31432' }} />
            Trailer Number
          </label>
          <input
            type="text"
            name="trailer"
            value={formData.trailer}
            onChange={handleChange}
          />
        </div>
      </div>

      <div className="form-section">
        <h2>
          <FaFileAlt style={{ marginRight: '8px', verticalAlign: 'middle', color: '#c31432' }} />
          Shipping Information (Optional)
        </h2>
        <div className="form-group">
          <label>
            <FaFileAlt style={{ marginRight: '6px', color: '#c31432' }} />
            DVL/Manifest Number
          </label>
          <input
            type="text"
            name="dvl_manifest_no"
            value={formData.dvl_manifest_no}
            onChange={handleChange}
          />
        </div>
        <div className="form-group">
          <label>
            <FaBox style={{ marginRight: '6px', color: '#c31432' }} />
            Shipper & Commodity
          </label>
          <input
            type="text"
            name="shipper_commodity"
            value={formData.shipper_commodity}
            onChange={handleChange}
          />
        </div>
      </div>

      {resetTrigger && (
        <button 
          type="submit" 
          className="submit-button" 
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <FaSpinner className="spinner-icon" style={{ color: '#ffffff' }} />
              Calculating Trip...
            </>
          ) : (
            <>
              <FaRoute style={{ color: '#ffffff' }} />
              Calculate Trip
            </>
          )}
        </button>
      )}
    </form>
  );
};

export default TripForm;

