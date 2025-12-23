import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from 'react-leaflet';
import { divIcon } from 'leaflet';
import * as L from 'leaflet';
import { RouteData, TimelineEvent } from '../types';
import { FaMap, FaRuler, FaGasPump, FaBed } from 'react-icons/fa';
import './MapDisplay.css';

import 'leaflet/dist/leaflet.css';
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const createCustomIcon = (symbol: string, color: string, size: number = 30) => {
  const iconMarkup = `
    <div style="
      background-color: ${color};
      border-radius: 50%;
      width: ${size}px;
      height: ${size}px;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 3px solid white;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      position: relative;
    ">
      <span style="
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        font-size: ${size * 0.6}px;
        line-height: 1;
        text-align: center;
      ">${symbol}</span>
    </div>
  `;

  return divIcon({
    html: iconMarkup,
    className: 'custom-marker',
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2]
  });
};

interface MapDisplayProps {
  route: RouteData;
  timeline: TimelineEvent[];
}

const MapBounds: React.FC<{ route: RouteData }> = ({ route }) => {
  const map = useMap();

  useEffect(() => {
    if (route.geometry.length > 0) {
      const bounds = L.latLngBounds(
        route.geometry.map(coord => [coord[1], coord[0]] as [number, number])
      );
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [map, route]);

  return null;
};

const MapDisplay: React.FC<MapDisplayProps> = ({ route, timeline }) => {
  const routeCoords = route.geometry.map(coord => [coord[1], coord[0]] as [number, number]);

  const restStops = timeline.filter(event => 
    event.status === 'off_duty' && event.description.includes('rest')
  );

  const filteredFuelStops = route.fuel_stops;

  const calculateRestBreakPositions = () => {
    if (restStops.length === 0 || routeCoords.length === 0) return [];

    const segmentDistances: number[] = [];
    let totalDistance = 0;
    for (let i = 0; i < routeCoords.length - 1; i++) {
      const coord1 = routeCoords[i];
      const coord2 = routeCoords[i + 1];
      const latDiff = coord2[0] - coord1[0];
      const lngDiff = coord2[1] - coord1[1];
      const distance = Math.sqrt(latDiff * latDiff + lngDiff * lngDiff) * 69;
      segmentDistances.push(distance);
      totalDistance += distance;
    }

    const AVERAGE_SPEED_MPH = 60;
    let cumulativeDistance = 0;
    let cumulativeTime = 0;
    const restBreakPositions: Array<{ position: [number, number], description: string }> = [];

    for (const event of timeline) {
      const eventDuration = event.duration || 0;
      
      if (event.status === 'driving') {
        const drivingDistance = eventDuration * AVERAGE_SPEED_MPH;
        cumulativeDistance += drivingDistance;
      }
      
      cumulativeTime += eventDuration;

      if (event.status === 'off_duty' && event.description.includes('rest')) {
        let remainingDistance = cumulativeDistance;
        let routeIndex = 0;
        let accumulatedRouteDistance = 0;
        
        for (let i = 0; i < segmentDistances.length; i++) {
          if (remainingDistance <= accumulatedRouteDistance + segmentDistances[i]) {
            routeIndex = i;
            remainingDistance = remainingDistance - accumulatedRouteDistance;
            break;
          }
          accumulatedRouteDistance += segmentDistances[i];
        }

        routeIndex = Math.min(routeIndex, routeCoords.length - 2);

        const segmentStart = routeCoords[routeIndex];
        const segmentEnd = routeCoords[Math.min(routeIndex + 1, routeCoords.length - 1)];
        const segmentDist = segmentDistances[routeIndex] || 1;
        const ratio = Math.max(0, Math.min(1, remainingDistance / segmentDist));
        
        const lat = segmentStart[0] + (segmentEnd[0] - segmentStart[0]) * ratio;
        const lng = segmentStart[1] + (segmentEnd[1] - segmentStart[1]) * ratio;
        
        restBreakPositions.push({
          position: [lat, lng],
          description: event.description
        });
      }
    }

    return restBreakPositions;
  };

  const restBreakPositions = calculateRestBreakPositions();

  return (
    <div className="map-container">
      <div className="map-header">
        <h2>
          <FaMap style={{ marginRight: '8px', verticalAlign: 'middle', color: '#c31432' }} />
          Route Map
        </h2>
        <div className="legend-inline">
          <div className="legend-item-inline">
            <div className="legend-icon-inline" style={{ backgroundColor: '#4CAF50' }}>
              <span style={{ fontSize: '16px' }}>📍</span>
            </div>
            <span>Start</span>
          </div>
          <div className="legend-item-inline">
            <div className="legend-icon-inline" style={{ backgroundColor: '#FF9800' }}>
              <span style={{ fontSize: '16px' }}>🚚</span>
            </div>
            <span>Pickup</span>
          </div>
          <div className="legend-item-inline">
            <div className="legend-icon-inline" style={{ backgroundColor: '#c31432' }}>
              <span style={{ fontSize: '16px' }}>📦</span>
            </div>
            <span>Dropoff</span>
          </div>
          <div className="legend-item-inline">
            <div className="legend-icon-inline" style={{ backgroundColor: '#FF9800' }}>
              <span style={{ fontSize: '16px' }}>⛽</span>
            </div>
            <span>Fuel</span>
          </div>
          <div className="legend-item-inline">
            <div className="legend-icon-inline" style={{ backgroundColor: '#4CAF50' }}>
              <span style={{ fontSize: '16px' }}>🛏️</span>
            </div>
            <span>Rest</span>
          </div>
        </div>
      </div>
      <MapContainer
        center={[route.start_coords[0], route.start_coords[1]] as L.LatLngExpression}
        zoom={6}
        style={{ height: '600px', width: '100%' }}
      >
        <MapBounds route={route} />
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        <Polyline 
          positions={routeCoords} 
          pathOptions={{ 
            color: '#c31432', 
            weight: 5,
            opacity: 0.8,
            lineCap: 'round',
            lineJoin: 'round'
          }}
        />
        
        <Marker 
          position={[route.start_coords[0], route.start_coords[1]] as L.LatLngExpression}
          icon={createCustomIcon(
            '📍',
            '#4CAF50',
            35
          )}
          zIndexOffset={1000}
        >
          <Popup>
            <div className="popup-content">
              <strong style={{ color: '#4CAF50', fontSize: '1.1em' }}>📍 Start Location</strong>
              <p style={{ margin: '5px 0' }}>Current Position</p>
            </div>
          </Popup>
        </Marker>
        
        <Marker 
          position={[route.pickup_coords[0], route.pickup_coords[1]] as L.LatLngExpression}
          icon={createCustomIcon(
            '🚚',
            '#FF9800',
            35
          )}
          zIndexOffset={1000}
        >
          <Popup>
            <div className="popup-content">
              <strong style={{ color: '#FF9800', fontSize: '1.1em' }}>🚚 Pickup Location</strong>
              <p style={{ margin: '5px 0' }}>Load Pickup Point</p>
            </div>
          </Popup>
        </Marker>
        
        <Marker 
          position={[route.dropoff_coords[0], route.dropoff_coords[1]] as L.LatLngExpression}
          icon={createCustomIcon(
            '📦',
            '#c31432',
            35
          )}
          zIndexOffset={1000}
        >
          <Popup>
            <div className="popup-content">
              <strong style={{ color: '#c31432', fontSize: '1.1em' }}>📦 Dropoff Location</strong>
              <p style={{ margin: '5px 0' }}>Final Destination</p>
            </div>
          </Popup>
        </Marker>
        {filteredFuelStops.map((stop, idx) => (
          <Marker 
            key={`fuel-${idx}`} 
            position={[stop.location[1], stop.location[0]] as L.LatLngExpression}
            icon={createCustomIcon(
              '⛽',
              '#FF9800',
              28
            )}
            zIndexOffset={100}
          >
            <Popup>
              <div className="popup-content">
                <strong style={{ color: '#FF9800', fontSize: '1.1em' }}>⛽ Fuel Stop {idx + 1}</strong>
                <p style={{ margin: '5px 0' }}>Distance: {stop.distance.toFixed(0)} miles</p>
                <p style={{ margin: '5px 0', fontSize: '0.9em', color: '#666' }}>Type: {stop.type || 'Standard'}</p>
              </div>
            </Popup>
          </Marker>
        ))}
        
        {restBreakPositions.map((restBreak, idx) => (
          <Marker 
            key={`rest-${idx}`} 
            position={restBreak.position as L.LatLngExpression}
            icon={createCustomIcon(
              '🛏️',
              '#4CAF50',
              28
            )}
            zIndexOffset={100}
          >
            <Popup>
              <div className="popup-content">
                <strong style={{ color: '#4CAF50', fontSize: '1.1em' }}>🛏️ Rest Break {idx + 1}</strong>
                <p style={{ margin: '5px 0' }}>{restBreak.description}</p>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
      
      <div className="map-info">
        <p>
          <FaRuler style={{ marginRight: '8px', color: '#e0e0e0' }} />
          <strong>Total Distance:</strong> {route.distance_miles.toFixed(2)} miles
        </p>
        <p>
          <FaGasPump style={{ marginRight: '8px', color: '#e0e0e0' }} />
          <strong>Fuel Stops:</strong> {filteredFuelStops.length > 0 ? filteredFuelStops.length : route.fuel_stops.length}
        </p>
        <p>
          <FaBed style={{ marginRight: '8px', color: '#e0e0e0' }} />
          <strong>Rest Breaks:</strong> {restStops.length}
        </p>
      </div>
    </div>
  );
};

export default MapDisplay;

