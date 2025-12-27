export interface TripRequest {
  current_location: string;
  pickup_location: string;
  dropoff_location: string;
  current_cycle_used: number;
  carrier_name?: string;
  main_office_address?: string;
  home_terminal_address?: string;
  driver_name?: string;
  co_driver_name?: string;
  truck_tractor?: string;
  trailer?: string;
  dvl_manifest_no?: string;
  shipper_commodity?: string;
  timezone?: string;
}

export interface IntermediateCityOnRoute {
  name: string;
  distance_miles: number;
  coordinates: [number, number];
  type: string;
  segment?: string;
}

export interface RouteData {
  distance_miles: number;
  geometry: number[][];
  fuel_stops: FuelStop[];
  start_coords: [number, number];
  pickup_coords: [number, number];
  dropoff_coords: [number, number];
  intermediate_cities?: IntermediateCityOnRoute[];
}

export interface FuelStop {
  location: [number, number];
  distance: number;
  type: string;
}

export interface TimelineEvent {
  time: string;
  status: string;
  description: string;
  duration: number;
  location: string | null;
}

export interface Compliance {
  compliant: boolean;
  total_on_duty: number;
  required_70_hour_hours: number;
  available_hours: number;
  exceeds_by: number;
}

export interface IntermediateCity {
  name: string;
  hours_into_day: number;
  distance: number;
  type?: 'pickup' | 'dropoff' | 'intermediate';
}

export interface LogSheet {
  date: string;
  from: string;
  to: string;
  total_miles_driving: number;
  total_mileage: string;
  carrier_name: string;
  main_office_address: string;
  home_terminal_address: string;
  truck_tractor_number: string;
  trailer_number: string;
  driver_name: string;
  co_driver_name: string;
  dvl_manifest_no: string;
  shipper_commodity: string;
  grid: {
    off_duty: Array<{ start: number; end: number }>;
    sleeper_berth: Array<{ start: number; end: number }>;
    driving: Array<{ start: number; end: number }>;
    on_duty_not_driving: Array<{ start: number; end: number }>;
  };
  totals: {
    off_duty: number;
    sleeper_berth: number;
    driving: number;
    on_duty_not_driving: number;
  };
  remarks: string[];
  recap: {
    on_duty_today: number;
    total_last_7_days: number;
    available_tomorrow_70: number;
    total_last_5_days: number;
  };
  intermediate_cities?: IntermediateCity[];
}

export interface TripResponse {
  route: RouteData;
  timeline: TimelineEvent[];
  compliance: Compliance;
  log_sheets: LogSheet[];
  summary: {
    total_driving_hours: number;
    total_on_duty_hours: number;
    estimated_arrival: string | null;
  };
}

