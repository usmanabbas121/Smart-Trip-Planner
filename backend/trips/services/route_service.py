import os
import time
import requests
from typing import List, Dict, Tuple, Optional
from geopy.distance import geodesic

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RouteService:
    OPENROUTE_SERVICE_BASE = "https://api.openrouteservice.org"
    OPENROUTE_GEOCODE_URL = f"{OPENROUTE_SERVICE_BASE}/geocode/search"
    OPENROUTE_ROUTE_URL = f"{OPENROUTE_SERVICE_BASE}/v2/directions/driving-car"
    
    LOCATIONIQ_GEOCODE_URL = "https://us1.locationiq.com/v1/search.php"
    NOMINATIM_GEOCODE_URL = "https://nominatim.openstreetmap.org/search"
    
    NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTE_SERVICE_API_KEY", "")
        self.geocode_errors = []
    
    STATE_ABBR = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
        "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
        "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
        "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
        "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
        "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
        "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
        "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
        "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
        "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
        "District of Columbia": "DC"
    }
    
    def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """Get area/city/county name from coordinates"""
        zoom_levels = [12, 10, 14, 8]
        
        for zoom in zoom_levels:
            try:
                params = {
                    "lat": lat,
                    "lon": lon,
                    "format": "json",
                    "zoom": zoom
                }
                headers = {
                    "User-Agent": "ELD-Trip-Planner/1.0",
                    "Accept": "application/json"
                }
                response = requests.get(
                    self.NOMINATIM_REVERSE_URL,
                    params=params,
                    headers=headers,
                    timeout=1.0,
                    verify=False
                )
                if response.status_code == 200:
                    data = response.json()
                    address = data.get("address", {})
                    
                    area = (address.get("city") or 
                           address.get("town") or 
                           address.get("village") or 
                           address.get("hamlet") or 
                           address.get("suburb") or 
                           address.get("municipality") or
                           address.get("borough") or
                           address.get("neighbourhood") or
                           address.get("neighborhood") or
                           address.get("county") or
                           address.get("state_district") or
                           address.get("region") or
                           "")
                    
                    state = address.get("state", "")
                    
                    if not area and state and "New York" in state:
                        area = address.get("borough") or address.get("county", "").replace(" County", "")
                    
                    if area and state:
                        state_abbr = self.STATE_ABBR.get(state, state[:2].upper())
                        return f"{area}, {state_abbr}"
                    elif area:
                        return area
                    elif state:
                        return state
                    
                    if zoom < 14:
                        continue
            except requests.exceptions.Timeout:
                continue
            except:
                continue
        
        return None
    
    def get_intermediate_cities_with_distance(self, route: Dict, interval_miles: float = 75.0) -> List[Dict]:
        """Get intermediate area names along the route at regular mile intervals with reverse geocoding"""
        areas = []
        if "geometry" not in route or "coordinates" not in route["geometry"]:
            return areas
        
        coordinates = route["geometry"]["coordinates"]
        total_distance = self.calculate_distance(route)
        
        if total_distance == 0 or len(coordinates) < 2:
            return areas
        
        accumulated = 0
        current_target = interval_miles
        max_points = 50
        last_area_name = None
        
        for i in range(len(coordinates) - 1):
            coord1 = coordinates[i]
            coord2 = coordinates[i + 1]
            segment_dist = geodesic((coord1[1], coord1[0]), (coord2[1], coord2[0])).miles
            accumulated += segment_dist
            
            if accumulated >= current_target:
                lat = coord2[1]
                lon = coord2[0]
                
                area_name = None
                try:
                    area_name = self.reverse_geocode(lat, lon)
                except:
                    pass
                
                if not area_name:
                    area_name = f"Route Point {len(areas) + 1} ({round(lat, 2)}, {round(lon, 2)})"
                
                if area_name != last_area_name:
                    areas.append({
                        "name": area_name,
                        "distance_miles": round(current_target, 1),
                        "coordinates": [lat, lon]
                    })
                    last_area_name = area_name
                
                current_target += interval_miles
                
                if len(areas) >= max_points:
                    break
        
        return areas
    
    def get_intermediate_cities_for_segment(self, start_coords: Tuple[float, float], end_coords: Tuple[float, float], 
                                           interval_miles: float = 50.0) -> List[Dict]:
        """Get intermediate cities between two points (for start->pickup and pickup->dropoff segments)"""
        areas = []
        total_distance = geodesic(start_coords, end_coords).miles
        
        if total_distance < interval_miles:
            return areas
        
        num_points = int(total_distance / interval_miles)
        if num_points > 10:
            num_points = 10
        
        for i in range(1, num_points + 1):
            fraction = i / (num_points + 1)
            lat = start_coords[0] + (end_coords[0] - start_coords[0]) * fraction
            lon = start_coords[1] + (end_coords[1] - start_coords[1]) * fraction
            
            if len(areas) > 0 and len(areas) % 5 == 0:
                time.sleep(0.05)
            area_name = self.reverse_geocode(lat, lon)
            
            if area_name:
                areas.append({
                    "name": area_name,
                    "distance_miles": round(total_distance * fraction, 1),
                    "coordinates": [lat, lon]
                })
        
        return areas
    
    def geocode(self, address: str, retries: int = 2) -> Optional[Tuple[float, float]]:
        if not address or not address.strip():
            return None
            
        address = address.strip()
        
        for attempt in range(retries):
            try:
                if attempt > 0:
                    time.sleep(0.2)
                
                params = {
                    "q": address,
                    "format": "json",
                    "limit": 1
                }
                
                response = requests.get(
                    self.LOCATIONIQ_GEOCODE_URL,
                    params=params,
                    headers={"Accept": "application/json"},
                    timeout=8,
                    verify=False
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 0 and "lat" in data[0] and "lon" in data[0]:
                        return (float(data[0]["lat"]), float(data[0]["lon"]))
            except:
                pass
        
        for attempt in range(retries):
            try:
                if attempt > 0:
                    time.sleep(0.2)
                
                params = {
                    "q": address,
                    "format": "json",
                    "limit": 1
                }
                
                headers = {
                    "User-Agent": "ELD-Trip-Planner/1.0",
                    "Accept": "application/json"
                }
                
                response = requests.get(
                    self.NOMINATIM_GEOCODE_URL,
                    params=params,
                    headers=headers,
                    timeout=8,
                    verify=False
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 0 and "lat" in data[0] and "lon" in data[0]:
                        return (float(data[0]["lat"]), float(data[0]["lon"]))
                elif response.status_code == 429:
                    if attempt < retries - 1:
                        time.sleep(0.5)
                        continue
            except requests.exceptions.Timeout:
                if attempt == retries - 1:
                    self.geocode_errors.append(f"{address}: Request timeout")
                continue
            except Exception as e:
                if attempt == retries - 1:
                    self.geocode_errors.append(f"{address}: {str(e)}")
                continue
        
        return None
    
    def get_route(self, start: Tuple[float, float], via: List[Tuple[float, float]], end: Tuple[float, float]) -> Optional[Dict]:
        coordinates = [[start[1], start[0]]]
        coordinates.extend([[v[1], v[0]] for v in via])
        coordinates.append([end[1], end[0]])
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            if self.api_key:
                headers["Authorization"] = self.api_key
            
            response = requests.post(
                self.OPENROUTE_ROUTE_URL,
                json={
                    "coordinates": coordinates,
                    "instructions": False,
                    "geometry": True
                },
                headers=headers,
                timeout=15,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                if "features" in data and len(data["features"]) > 0:
                    return data["features"][0]
            elif response.status_code == 401 or response.status_code == 403:
                return self._calculate_simple_route(start, via, end)
            elif response.status_code == 429:
                time.sleep(0.5)
                response = requests.post(
                    self.OPENROUTE_ROUTE_URL,
                    json={"coordinates": coordinates},
                    headers=headers,
                    timeout=15,
                    verify=False
                )
                if response.status_code == 200:
                    data = response.json()
                if "features" in data and len(data["features"]) > 0:
                    return data["features"][0]
            else:
                return self._calculate_simple_route(start, via, end)
        except requests.exceptions.Timeout:
            return self._calculate_simple_route(start, via, end)
        except Exception as e:
            return self._calculate_simple_route(start, via, end)
        
        return None
    
    def _calculate_simple_route(self, start: Tuple[float, float], via: List[Tuple[float, float]], end: Tuple[float, float]) -> Optional[Dict]:
        try:
            waypoints = [start]
            waypoints.extend(via)
            waypoints.append(end)
            
            total_distance_meters = 0
            geometry = []
            
            for i in range(len(waypoints) - 1):
                p1 = waypoints[i]
                p2 = waypoints[i + 1]
                segment_dist = geodesic(p1, p2).miles
                total_distance_meters += segment_dist * 1609.34
                
                geometry.append([p1[1], p1[0]])
                
                num_intermediate = max(1, int(segment_dist / 50))
                for j in range(1, num_intermediate):
                    fraction = j / num_intermediate
                    lat = p1[0] + (p2[0] - p1[0]) * fraction
                    lon = p1[1] + (p2[1] - p1[1]) * fraction
                    geometry.append([lon, lat])
            
            geometry.append([waypoints[-1][1], waypoints[-1][0]])
            
            return {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": geometry
                },
                "properties": {
                    "segments": [{
                        "distance": total_distance_meters,
                        "duration": total_distance_meters / 20.0
                    }]
                }
            }
        except Exception:
            return None
    
    def calculate_distance(self, route: Dict) -> float:
        if "properties" in route and "segments" in route["properties"]:
            total_distance = 0
            for segment in route["properties"]["segments"]:
                if "distance" in segment:
                    total_distance += segment["distance"]
            return total_distance / 1609.34
        return 0.0
    
    def calculate_duration(self, route: Dict) -> float:
        if "properties" in route and "segments" in route["properties"]:
            total_duration = 0
            for segment in route["properties"]["segments"]:
                if "duration" in segment:
                    total_duration += segment["duration"]
            return total_duration / 3600.0
        return 0.0
    
    def get_route_geometry(self, route: Dict) -> List[List[float]]:
        if "geometry" in route and "coordinates" in route["geometry"]:
            return route["geometry"]["coordinates"]
        return []
    
    def find_fuel_stops(self, route: Dict, interval_miles: float = 1000.0) -> List[Dict]:
        fuel_stops = []
        if "geometry" not in route or "coordinates" not in route["geometry"]:
            return fuel_stops
        
        coordinates = route["geometry"]["coordinates"]
        total_distance = self.calculate_distance(route)
        
        if total_distance == 0:
            return fuel_stops
        
        if len(coordinates) < 10:
            interpolated_coords = []
            for i in range(len(coordinates) - 1):
                coord1 = coordinates[i]
                coord2 = coordinates[i + 1]
                interpolated_coords.append(coord1)
                segment_dist = geodesic((coord1[1], coord1[0]), (coord2[1], coord2[0])).miles
                num_points = max(1, int(segment_dist / 50))
                for j in range(1, num_points):
                    ratio = j / num_points
                    lat = coord1[1] + (coord2[1] - coord1[1]) * ratio
                    lon = coord1[0] + (coord2[0] - coord1[0]) * ratio
                    interpolated_coords.append([lon, lat])
            interpolated_coords.append(coordinates[-1])
            coordinates = interpolated_coords
        
        accumulated_distance = 0.0
        current_interval = interval_miles
        
        for i in range(len(coordinates) - 1):
            coord1 = coordinates[i]
            coord2 = coordinates[i + 1]
            
            segment_distance = geodesic(
                (coord1[1], coord1[0]),
                (coord2[1], coord2[0])
            ).miles
            
            accumulated_distance += segment_distance
            
            if accumulated_distance >= current_interval:
                fuel_stops.append({
                    "location": [coord2[0], coord2[1]],
                    "distance": round(current_interval, 2),
                    "type": "fuel"
                })
                current_interval += interval_miles
        
        return fuel_stops

