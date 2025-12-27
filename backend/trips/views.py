import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from .serializers import TripRequestSerializer
from .services.route_service import RouteService
from .services.hos_calculator import HOSCalculator
from .services.log_generator import LogGenerator


class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            "status": "ok",
            "message": "Django backend is running",
            "service": "ELD Trip Planner API"
        })


class CalculateTripView(APIView):
    def post(self, request):
        serializer = TripRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        route_service = RouteService()
        
        start_coords = route_service.geocode(data["current_location"])
        time.sleep(0.3)
        pickup_coords = route_service.geocode(data["pickup_location"])
        time.sleep(0.3)
        dropoff_coords = route_service.geocode(data["dropoff_location"])
        
        if start_coords and pickup_coords:
            from geopy.distance import geodesic
            distance = geodesic(start_coords, pickup_coords).miles
            if distance < 0.1:  # Less than 0.1 miles apart
                return Response(
                    {"error": f"Pickup location is too close to current location (less than 0.1 miles). Please ensure pickup is a different location."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        failed_locations = []
        if not start_coords:
            failed_locations.append(f"Current Location: '{data['current_location']}'")
        if not pickup_coords:
            failed_locations.append(f"Pickup Location: '{data['pickup_location']}'")
        if not dropoff_coords:
            failed_locations.append(f"Dropoff Location: '{data['dropoff_location']}'")
        
        if failed_locations:
            error_msg = f"Could not geocode the following locations: {', '.join(failed_locations)}. "
            error_msg += "Please try more specific addresses (e.g., 'City, State' or 'Street Address, City, State, ZIP')."
            if route_service.geocode_errors:
                error_msg += f" Errors: {'; '.join(route_service.geocode_errors[:3])}"
            return Response(
                {"error": error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        route = route_service.get_route(start_coords, [pickup_coords], dropoff_coords)
        
        if not route:
            return Response(
                {"error": "Could not calculate route"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        total_distance = route_service.calculate_distance(route)
        route_geometry = route_service.get_route_geometry(route)
        fuel_stops = route_service.find_fuel_stops(route)
        
        from geopy.distance import geodesic
        route_coords = route_service.get_route_geometry(route)
        
        pickup_on_route_index = 0
        min_distance_to_pickup = float('inf')
        for i, coord in enumerate(route_coords):
            dist = geodesic((coord[1], coord[0]), pickup_coords).miles
            if dist < min_distance_to_pickup:
                min_distance_to_pickup = dist
                pickup_on_route_index = i
        
        start_to_pickup_distance = 0.0
        for i in range(pickup_on_route_index):
            if i + 1 < len(route_coords):
                coord1 = route_coords[i]
                coord2 = route_coords[i + 1]
                start_to_pickup_distance += geodesic((coord1[1], coord1[0]), (coord2[1], coord2[0])).miles
        
        route_intermediate_cities = route_service.get_intermediate_cities_with_distance(route, interval_miles=100.0)
        
        for city in route_intermediate_cities:
            if city["distance_miles"] < start_to_pickup_distance:
                city["segment"] = "start_to_pickup"
            else:
                city["segment"] = "pickup_to_dropoff"
        
        intermediate_areas = route_service.get_intermediate_cities_with_distance(route, interval_miles=50.0)
        
        start_name = data["current_location"].split(',')[0]
        pickup_name = data["pickup_location"].split(',')[0]
        dropoff_name = data["dropoff_location"].split(',')[0]
        
        cities_before_pickup = [area for area in intermediate_areas if area["distance_miles"] < start_to_pickup_distance]
        cities_after_pickup = [area for area in intermediate_areas if area["distance_miles"] >= start_to_pickup_distance]
        
        intermediate_cities = [
            {"name": start_name, "distance_miles": 0.0, "type": "start"}
        ] + [dict(area, type="intermediate") for area in cities_before_pickup] + [
            {"name": pickup_name, "distance_miles": round(start_to_pickup_distance, 1), "type": "pickup"}
        ] + [dict(area, type="intermediate") for area in cities_after_pickup] + [
            {"name": dropoff_name, "distance_miles": round(total_distance, 1), "type": "dropoff"}
        ]
        
        if len(intermediate_areas) < 10 and total_distance > 300:
            intermediate_areas_dense = route_service.get_intermediate_cities_with_distance(route, interval_miles=30.0)
            if len(intermediate_areas_dense) > len(intermediate_areas):
                intermediate_areas = intermediate_areas_dense
                cities_before_pickup = [area for area in intermediate_areas if area["distance_miles"] < start_to_pickup_distance]
                cities_after_pickup = [area for area in intermediate_areas if area["distance_miles"] >= start_to_pickup_distance]
                intermediate_cities = [
                    {"name": start_name, "distance_miles": 0.0, "type": "start"}
                ] + [dict(area, type="intermediate") for area in cities_before_pickup] + [
                    {"name": pickup_name, "distance_miles": round(start_to_pickup_distance, 1), "type": "pickup"}
                ] + [dict(area, type="intermediate") for area in cities_after_pickup] + [
                    {"name": dropoff_name, "distance_miles": round(total_distance, 1), "type": "dropoff"}
                ]
        
        timezone_str = data.get("timezone", "UTC")
        try:
            tz = ZoneInfo(timezone_str)
        except:
            tz = ZoneInfo("UTC")
        
        start_time = datetime.now(tz)
        
        hos_calculator = HOSCalculator(
            current_cycle_used=data["current_cycle_used"],
            start_time=start_time
        )
        
        trip_result = hos_calculator.calculate_trip_timeline(
            total_distance_miles=total_distance
        )
        
        carrier_info = {
            "name": data.get("carrier_name", ""),
            "main_office_address": data.get("main_office_address", ""),
            "home_terminal_address": data.get("home_terminal_address", ""),
            "driver_name": data.get("driver_name", ""),
            "co_driver_name": data.get("co_driver_name", ""),
            "dvl_manifest_no": data.get("dvl_manifest_no", ""),
            "shipper_commodity": data.get("shipper_commodity", ""),
            "from": data["current_location"],
            "to": data["dropoff_location"],
            "current_cycle_used": data["current_cycle_used"]
        }
        
        vehicle_info = {
            "truck_tractor": data.get("truck_tractor", ""),
            "trailer": data.get("trailer", ""),
            "total_mileage": ""
        }
        
        log_generator = LogGenerator()
        log_sheets = log_generator.generate_log_sheets(
            timeline=trip_result["timeline"],
            start_time=start_time,
            total_miles=total_distance,
            carrier_info=carrier_info,
            vehicle_info=vehicle_info,
            intermediate_cities=intermediate_cities
        )
        
        return Response({
            "route": {
                "distance_miles": round(total_distance, 2),
                "geometry": route_geometry,
                "fuel_stops": fuel_stops,
                "start_coords": start_coords,
                "pickup_coords": pickup_coords,
                "dropoff_coords": dropoff_coords,
                "intermediate_cities": route_intermediate_cities
            },
            "timeline": [
                {
                    "time": event["time"].isoformat(),
                    "status": event["status"],
                    "description": event["description"],
                    "duration": event["duration"],
                    "location": event.get("location")
                }
                for event in trip_result["timeline"]
            ],
            "compliance": trip_result["compliance"],
            "log_sheets": log_sheets,
            "summary": {
                "total_driving_hours": round(trip_result["total_driving_hours"], 2),
                "total_on_duty_hours": round(trip_result["total_on_duty_hours"], 2),
                "estimated_arrival": (
                    trip_result["timeline"][-1]["time"] + 
                    timedelta(hours=trip_result["timeline"][-1].get("duration", 0))
                ).isoformat() if trip_result["timeline"] else None
            }
        })
