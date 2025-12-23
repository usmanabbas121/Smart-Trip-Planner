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


class CalculateTripView(APIView):
    def post(self, request):
        serializer = TripRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        route_service = RouteService()
        
        start_coords = route_service.geocode(data["current_location"])
        time.sleep(1.2)
        pickup_coords = route_service.geocode(data["pickup_location"])
        time.sleep(1.2)
        dropoff_coords = route_service.geocode(data["dropoff_location"])
        
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
            vehicle_info=vehicle_info
        )
        
        return Response({
            "route": {
                "distance_miles": round(total_distance, 2),
                "geometry": route_geometry,
                "fuel_stops": fuel_stops,
                "start_coords": start_coords,
                "pickup_coords": pickup_coords,
                "dropoff_coords": dropoff_coords
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
