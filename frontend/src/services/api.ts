import axios, { AxiosError } from 'axios';
import { TripRequest, TripResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const calculateTrip = async (data: TripRequest): Promise<TripResponse> => {
  try {
    const response = await axios.post<TripResponse>(
      `${API_BASE_URL}/api/calculate-trip/`,
      data
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
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
        throw new Error('Unable to connect to server. Please check if the backend is running.');
      }
    }
    throw error;
  }
};

