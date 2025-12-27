import axios, { AxiosError } from 'axios';
import { TripRequest, TripResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const calculateTrip = async (data: TripRequest, retries: number = 3): Promise<TripResponse> => {
  let lastError: any = null;
  
  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      const response = await axios.post<TripResponse>(
        `${API_BASE_URL}/api/calculate-trip/`,
        data,
        {
          timeout: 120000, // 2 minutes timeout for long calculations
        }
      );
      return response.data;
    } catch (error) {
      lastError = error;
      
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError;
        
        // If it's a connection error and we have retries left, wait and retry
        if (axiosError.request && !axiosError.response && attempt < retries - 1) {
          // Wait before retrying (exponential backoff)
          const waitTime = Math.min(1000 * Math.pow(2, attempt), 5000);
          await new Promise(resolve => setTimeout(resolve, waitTime));
          continue; // Retry
        }
        
        if (axiosError.response) {
          const errorData = axiosError.response.data as any;
          if (errorData?.error) {
            throw new Error(errorData.error);
          } else if (errorData && typeof errorData === 'object') {
            const errorMessages = Object.entries(errorData)
              .map(([key, value]) => {
                if (Array.isArray(value)) {
                  return `${key}: ${value.join(', ')}`;
                }
                return `${key}: ${value}`;
              })
              .join('; ');
            throw new Error(errorMessages || 'Validation error');
          }
          throw new Error(`Server error: ${axiosError.response.status}`);
        } else if (axiosError.request) {
          // Connection error - only show if all retries failed
          if (attempt === retries - 1) {
            throw new Error('Unable to connect to server. Please check if the backend is running.');
          }
        }
      } else {
        // Non-axios error, throw immediately
        throw error;
      }
    }
  }
  
  // If we get here, all retries failed
  throw lastError;
};

