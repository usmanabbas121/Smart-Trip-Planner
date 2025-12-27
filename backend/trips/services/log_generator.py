from datetime import datetime, timedelta
from typing import List, Dict, Optional
from decimal import Decimal, ROUND_HALF_UP


class LogGenerator:
    MINUTES_PER_DAY = 24 * 60
    AVERAGE_SPEED_MPH = 60.0
    
    def _calculate_city_times(self, timeline: List[Dict], intermediate_cities: List[Dict]) -> List[Dict]:
        """Calculate actual times when each city distance is reached based on timeline driving segments"""
        cities_with_times = []
        
        if not intermediate_cities:
            return cities_with_times
        
        sorted_cities = sorted(intermediate_cities, key=lambda x: x["distance_miles"])
        
        first_driving_event = next((e for e in timeline if e["status"] == "driving"), None)
        first_event = timeline[0] if timeline else None
        pickup_city = next((c for c in sorted_cities if c.get("type") == "pickup"), None)
        start_to_pickup_distance = pickup_city["distance_miles"] if pickup_city else 0.0
        
        total_driving_miles = sum(
            event.get("duration", 0) * self.AVERAGE_SPEED_MPH 
            for event in timeline 
            if event.get("status") == "driving"
        )
        
        if start_to_pickup_distance > 0 and first_driving_event and first_event:
            hours_to_pickup = start_to_pickup_distance / self.AVERAGE_SPEED_MPH
            trip_start_time = first_event["time"]
        else:
            hours_to_pickup = 0
            trip_start_time = first_driving_event["time"] if first_driving_event else None
        
        cumulative_driving_miles = 0.0
        city_index = 0
        last_driving_end_time = None
        
        for event in timeline:
            if event["status"] != "driving":
                continue
            
            driving_hours = event.get("duration", 0)
            driving_miles = driving_hours * self.AVERAGE_SPEED_MPH
            event_start_time = event["time"]
            last_driving_end_time = event_start_time + timedelta(hours=driving_hours)
            
            while city_index < len(sorted_cities):
                city = sorted_cities[city_index]
                city_distance_from_start = city["distance_miles"]
                
                if city_distance_from_start == 0 and city.get("type") == "start":
                    if trip_start_time:
                        cities_with_times.append({
                            "name": city["name"],
                            "distance_miles": 0,
                            "reached_time": trip_start_time,
                            "type": "start"
                        })
                    city_index += 1
                    continue
                
                if city.get("type") == "pickup" and first_driving_event:
                    cities_with_times.append({
                        "name": city["name"],
                        "distance_miles": city_distance_from_start,
                        "reached_time": first_driving_event["time"],
                        "type": "pickup"
                    })
                    city_index += 1
                    continue
                
                if city_distance_from_start < start_to_pickup_distance:
                    if trip_start_time and start_to_pickup_distance > 0:
                        hours_from_start = city_distance_from_start / self.AVERAGE_SPEED_MPH
                        city_reached_time = trip_start_time + timedelta(hours=hours_from_start)
                        
                        cities_with_times.append({
                            "name": city["name"],
                            "distance_miles": city_distance_from_start,
                            "reached_time": city_reached_time,
                            "type": city.get("type", "intermediate")
                        })
                    else:
                        if trip_start_time:
                            cities_with_times.append({
                                "name": city["name"],
                                "distance_miles": city_distance_from_start,
                                "reached_time": trip_start_time,
                                "type": city.get("type", "intermediate")
                            })
                    city_index += 1
                    continue
                
                distance_from_pickup = city_distance_from_start - start_to_pickup_distance
                
                if cumulative_driving_miles < distance_from_pickup <= cumulative_driving_miles + driving_miles:
                    miles_into_segment = distance_from_pickup - cumulative_driving_miles
                    hours_into_segment = miles_into_segment / self.AVERAGE_SPEED_MPH
                    city_reached_time = event_start_time + timedelta(hours=hours_into_segment)
                    
                    event_end = event_start_time + timedelta(hours=driving_hours)
                    if event_start_time <= city_reached_time <= event_end:
                        cities_with_times.append({
                            "name": city["name"],
                            "distance_miles": city_distance_from_start,
                            "reached_time": city_reached_time,
                            "type": city.get("type", "intermediate")
                        })
                    city_index += 1
                elif distance_from_pickup > cumulative_driving_miles + driving_miles:
                    break
                else:
                    city_index += 1
            
            cumulative_driving_miles += driving_miles
            
            if city_index >= len(sorted_cities):
                break
        
        while city_index < len(sorted_cities):
            city = sorted_cities[city_index]
            city_distance_from_start = city["distance_miles"]
            
            if city_distance_from_start >= start_to_pickup_distance:
                distance_from_pickup = city_distance_from_start - start_to_pickup_distance
                
                temp_cumulative = 0.0
                found = False
                for event in timeline:
                    if event["status"] == "driving":
                        driving_miles = event.get("duration", 0) * self.AVERAGE_SPEED_MPH
                        if temp_cumulative + driving_miles >= distance_from_pickup:
                            miles_into_segment = distance_from_pickup - temp_cumulative
                            hours_into_segment = miles_into_segment / self.AVERAGE_SPEED_MPH
                            city_reached_time = event["time"] + timedelta(hours=hours_into_segment)
                            
                            event_end = event["time"] + timedelta(hours=event.get("duration", 0))
                            if event["time"] <= city_reached_time <= event_end:
                                cities_with_times.append({
                                    "name": city["name"],
                                    "distance_miles": city_distance_from_start,
                                    "reached_time": city_reached_time,
                                    "type": city.get("type", "intermediate")
                                })
                                found = True
                                break
                        temp_cumulative += driving_miles
                
                if not found:
                    temp_cumulative = 0.0
                    for event in timeline:
                        if event["status"] == "driving":
                            driving_miles = event.get("duration", 0) * self.AVERAGE_SPEED_MPH
                            
                            if temp_cumulative < distance_from_pickup <= temp_cumulative + driving_miles:
                                miles_into_segment = distance_from_pickup - temp_cumulative
                                hours_into_segment = miles_into_segment / self.AVERAGE_SPEED_MPH
                                city_reached_time = event["time"] + timedelta(hours=hours_into_segment)
                                
                                event_end = event["time"] + timedelta(hours=event.get("duration", 0))
                                if event["time"] <= city_reached_time <= event_end:
                                    cities_with_times.append({
                                        "name": city["name"],
                                        "distance_miles": city_distance_from_start,
                                        "reached_time": city_reached_time,
                                        "type": city.get("type", "intermediate")
                                    })
                                    found = True
                                    break
                            
                            temp_cumulative += driving_miles
                    
                    if not found and distance_from_pickup <= total_driving_miles and first_driving_event and last_driving_end_time:
                        distance_ratio = distance_from_pickup / total_driving_miles if total_driving_miles > 0 else 0
                        timeline_start = first_driving_event["time"]
                        timeline_end = last_driving_end_time
                        timeline_duration = (timeline_end - timeline_start).total_seconds() / 3600.0
                        
                        estimated_hours = distance_ratio * timeline_duration
                        city_reached_time = timeline_start + timedelta(hours=estimated_hours)
                        
                        closest_segment = None
                        min_time_diff = float('inf')
                        for event in timeline:
                            if event["status"] == "driving":
                                event_start = event["time"]
                                event_end = event["time"] + timedelta(hours=event.get("duration", 0))
                                if event_start <= city_reached_time <= event_end:
                                    closest_segment = event
                                    break
                                if event_start <= city_reached_time:
                                    time_diff = (city_reached_time - event_start).total_seconds()
                                    if time_diff < min_time_diff:
                                        min_time_diff = time_diff
                                        closest_segment = event
                        
                        if closest_segment:
                            event_start = closest_segment["time"]
                            event_end = event_start + timedelta(hours=closest_segment.get("duration", 0))
                            if city_reached_time < event_start:
                                city_reached_time = event_start
                            elif city_reached_time > event_end:
                                city_reached_time = event_end
                            
                            cities_with_times.append({
                                "name": city["name"],
                                "distance_miles": city_distance_from_start,
                                "reached_time": city_reached_time,
                                "type": city.get("type", "intermediate")
                            })
                            found = True
                        elif last_driving_end_time:
                            cities_with_times.append({
                                "name": city["name"],
                                "distance_miles": city_distance_from_start,
                                "reached_time": last_driving_end_time,
                                "type": city.get("type", "intermediate")
                            })
                            found = True
            
            city_index += 1
        
        return cities_with_times
    
    def generate_log_sheets(
        self,
        timeline: List[Dict],
        start_time: datetime,
        total_miles: float,
        carrier_info: Dict,
        vehicle_info: Dict,
        intermediate_cities: List[Dict] = None
    ) -> List[Dict]:
        log_sheets = []
        end_time = timeline[-1]["time"] + timedelta(hours=timeline[-1].get("duration", 0))
        
        cities_with_times = self._calculate_city_times(timeline, intermediate_cities or [])
        
        all_cities_for_remarks = []
        for city_with_time in cities_with_times:
            all_cities_for_remarks.append({
                "name": city_with_time["name"],
                "hours_into_day": 0,
                "distance": city_with_time["distance_miles"],
                "type": city_with_time.get("type", "intermediate")
            })
        
        total_days = (end_time.date() - start_time.replace(hour=0, minute=0, second=0, microsecond=0).date()).days + 1
        
        current_day_start = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        day_index = 0
        last_city_from_previous_day = None
        
        while current_day_start < end_time:
            next_day_start = current_day_start + timedelta(days=1)
            is_last_day = (day_index == total_days - 1) or (next_day_start >= end_time)
            
            sheet_timeline = []
            for event in timeline:
                event_start = event["time"]
                event_end = event_start + timedelta(hours=event.get("duration", 0))
                if event_start < next_day_start and event_end > current_day_start:
                    day_event = event.copy()
                    if event_start < current_day_start:
                        day_event["time"] = current_day_start
                        original_duration = event.get("duration", 0)
                        elapsed_before_day = (current_day_start - event_start).total_seconds() / 3600.0
                        day_event["duration"] = max(0, original_duration - elapsed_before_day)
                    else:
                        day_event["time"] = event_start
                    if event_end > next_day_start:
                        day_event["duration"] = min(day_event.get("duration", 0), (next_day_start - day_event["time"]).total_seconds() / 3600.0)
                    if day_event.get("duration", 0) > 0:
                        sheet_timeline.append(day_event)
            
            if not sheet_timeline and current_day_start < end_time:
                sheet_timeline = [{
                    "time": current_day_start,
                    "status": "off_duty",
                    "description": "Off duty",
                    "duration": 24.0,
                    "location": None
                }]
            
            next_day_start = current_day_start + timedelta(days=1)
            is_last_day = (day_index == total_days - 1) or (next_day_start >= end_time)
            
            day_cities = []
            
            for city_with_time in cities_with_times:
                city_reached_time = city_with_time["reached_time"]
                city_date = city_reached_time.date()
                day_date = current_day_start.date()
                next_day_date = next_day_start.date()
                
                if day_date <= city_date < next_day_date:
                    if city_date == day_date:
                        hours_into_day = city_reached_time.hour + city_reached_time.minute / 60.0
                    else:
                        hours_into_day = city_reached_time.hour + city_reached_time.minute / 60.0
                    
                    day_cities.append({
                        "name": city_with_time["name"],
                        "hours_into_day": hours_into_day,
                        "distance": city_with_time["distance_miles"],
                        "type": city_with_time.get("type", "intermediate")
                    })
                elif abs((city_date - day_date).days) == 1:
                    if city_date > day_date and city_reached_time.hour < 1:
                        hours_into_day = city_reached_time.hour + city_reached_time.minute / 60.0
                        day_cities.append({
                            "name": city_with_time["name"],
                            "hours_into_day": hours_into_day,
                            "distance": city_with_time["distance_miles"],
                            "type": city_with_time.get("type", "intermediate")
                        })
                    elif city_date < day_date and city_reached_time.hour >= 23:
                        hours_into_day = city_reached_time.hour + city_reached_time.minute / 60.0
                        day_cities.append({
                            "name": city_with_time["name"],
                            "hours_into_day": hours_into_day,
                            "distance": city_with_time["distance_miles"],
                            "type": city_with_time.get("type", "intermediate")
                        })
            
            if not day_cities and sheet_timeline:
                dropoff_event = next((e for e in sheet_timeline if e.get("description", "").lower() == "dropoff"), None)
                if dropoff_event:
                    dropoff_time = dropoff_event["time"]
                    hours_into_day = (dropoff_time - current_day_start).total_seconds() / 3600.0
                    if 0 <= hours_into_day < 24:
                        dropoff_location = carrier_info.get("to", "")
                        if dropoff_location:
                            location_parts = dropoff_location.split(",")
                            city_name = location_parts[0].strip() if location_parts else dropoff_location
                            
                            dropoff_city = next((c for c in cities_with_times if c.get("type") == "dropoff"), None)
                            if dropoff_city:
                                city_name = dropoff_city.get("name", city_name)
                            
                            day_cities.append({
                                "name": city_name,
                                "hours_into_day": hours_into_day,
                                "distance": 0,
                                "type": "dropoff"
                            })
            
            day_cities.sort(key=lambda x: x["hours_into_day"])
            
            if day_index == 0:
                day_from_location = carrier_info.get("from", "")
            else:
                day_from_location = last_city_from_previous_day if last_city_from_previous_day else carrier_info.get("from", "")
            
            if is_last_day:
                day_to_location = carrier_info.get("to", "")
            else:
                if day_cities:
                    sorted_day_cities = sorted(day_cities, key=lambda x: x["hours_into_day"])
                    day_to_location = sorted_day_cities[-1]["name"]
                else:
                    day_to_location = last_city_from_previous_day if last_city_from_previous_day else carrier_info.get("from", "")
            
            day_carrier_info = carrier_info.copy()
            day_carrier_info["from"] = day_from_location
            day_carrier_info["to"] = day_to_location
            
            all_cities_for_day = []
            for city_with_time in cities_with_times:
                city_reached_time = city_with_time["reached_time"]
                city_date = city_reached_time.date()
                day_date = current_day_start.date()
                next_day_date = next_day_start.date()
                
                if day_date <= city_date < next_day_date:
                    if city_date == day_date:
                        hours_into_day = city_reached_time.hour + city_reached_time.minute / 60.0
                    else:
                        hours_into_day = city_reached_time.hour + city_reached_time.minute / 60.0
                    
                    all_cities_for_day.append({
                        "name": city_with_time["name"],
                        "hours_into_day": hours_into_day,
                        "distance": city_with_time["distance_miles"],
                        "type": city_with_time.get("type", "intermediate")
                    })
                elif abs((city_date - day_date).days) == 1:
                    if city_date > day_date and city_reached_time.hour < 1:
                        hours_into_day = city_reached_time.hour + city_reached_time.minute / 60.0
                        all_cities_for_day.append({
                            "name": city_with_time["name"],
                            "hours_into_day": hours_into_day,
                            "distance": city_with_time["distance_miles"],
                            "type": city_with_time.get("type", "intermediate")
                        })
                    elif city_date < day_date and city_reached_time.hour >= 23:
                        hours_into_day = city_reached_time.hour + city_reached_time.minute / 60.0
                        all_cities_for_day.append({
                            "name": city_with_time["name"],
                            "hours_into_day": hours_into_day,
                            "distance": city_with_time["distance_miles"],
                            "type": city_with_time.get("type", "intermediate")
                        })
            
            all_cities_for_remarks_context = []
            for city_with_time in cities_with_times:
                city_reached_time = city_with_time["reached_time"]
                city_date = city_reached_time.date()
                day_date = current_day_start.date()
                next_day_date = next_day_start.date()
                
                if day_date <= city_date < next_day_date:
                    hours_into_day = city_reached_time.hour + city_reached_time.minute / 60.0
                else:
                    hours_into_day = 12.0
                
                all_cities_for_remarks_context.append({
                    "name": city_with_time["name"],
                    "hours_into_day": hours_into_day,
                    "distance": city_with_time["distance_miles"],
                    "type": city_with_time.get("type", "intermediate")
                })
            
            log_sheet = self._generate_single_log_sheet(
                sheet_timeline,
                current_day_start,
                next_day_start,
                total_miles if day_index == 0 else 0.0,
                day_carrier_info,
                vehicle_info,
                day_index,
                day_cities,
                all_cities_for_remarks_context
            )
            
            log_sheets.append(log_sheet)
            
            if day_cities:
                sorted_day_cities = sorted(day_cities, key=lambda x: x["hours_into_day"])
                last_city_from_previous_day = sorted_day_cities[-1]["name"]
            elif day_to_location and day_to_location != carrier_info.get("from", ""):
                last_city_from_previous_day = day_to_location
            
            current_day_start = next_day_start
            day_index += 1
        
        return log_sheets
    
    def _generate_single_log_sheet(
        self,
        timeline: List[Dict],
        start_time: datetime,
        end_time: datetime,
        total_miles: float,
        carrier_info: Dict,
        vehicle_info: Dict,
        day_index: int,
        intermediate_cities: List[Dict] = None,
        all_intermediate_cities: List[Dict] = None
    ) -> Dict:
        grid = self._generate_grid(timeline, start_time)
        totals = self._calculate_totals(timeline)
        remarks = self._generate_remarks(timeline, intermediate_cities or [], start_time, all_intermediate_cities or [], carrier_info)
        
        miles_today = totals.get("driving", 0.0) * 60.0
        
        return {
            "date": start_time.strftime("%m/%d/%Y"),
            "from": carrier_info.get("from", ""),
            "to": carrier_info.get("to", ""),
            "total_miles_driving": round(miles_today, 1),
            "total_mileage": vehicle_info.get("total_mileage", ""),
            "carrier_name": carrier_info.get("name", ""),
            "main_office_address": carrier_info.get("main_office_address", ""),
            "home_terminal_address": carrier_info.get("home_terminal_address", ""),
            "truck_tractor_number": vehicle_info.get("truck_tractor", ""),
            "trailer_number": vehicle_info.get("trailer", ""),
            "driver_name": carrier_info.get("driver_name", ""),
            "co_driver_name": carrier_info.get("co_driver_name", ""),
            "dvl_manifest_no": carrier_info.get("dvl_manifest_no", ""),
            "shipper_commodity": carrier_info.get("shipper_commodity", ""),
            "grid": grid,
            "totals": totals,
            "remarks": remarks,
            "recap": self._calculate_recap(totals, carrier_info.get("current_cycle_used", 0)),
            "intermediate_cities": intermediate_cities or []
        }
    
    def _generate_grid(
        self,
        timeline: List[Dict],
        day_start: datetime
    ) -> Dict:
        grid = {
            "off_duty": [],
            "sleeper_berth": [],
            "driving": [],
            "on_duty_not_driving": []
        }
        
        day_end = day_start + timedelta(days=1)
        sorted_timeline = sorted(timeline, key=lambda x: x["time"])
        last_end_minute = 0
        
        for event in sorted_timeline:
            event_start = event["time"]
            event_duration_hours = event.get("duration", 0)
            event_end = event_start + timedelta(hours=event_duration_hours)
            
            actual_start = max(event_start, day_start)
            actual_end = min(event_end, day_end)
            
            if actual_start >= actual_end:
                continue
            
            start_minute = int((actual_start - day_start).total_seconds() / 60)
            end_minute = int((actual_end - day_start).total_seconds() / 60)
            end_minute = min(end_minute, self.MINUTES_PER_DAY)
            
            if start_minute < last_end_minute:
                start_minute = last_end_minute
            
            if start_minute >= end_minute:
                continue
                
            last_end_minute = end_minute
            
            status = event["status"]
            if status == "off_duty":
                grid["off_duty"].append({"start": start_minute, "end": end_minute})
            elif status == "sleeper_berth":
                grid["sleeper_berth"].append({"start": start_minute, "end": end_minute})
            elif status == "driving":
                grid["driving"].append({"start": start_minute, "end": end_minute})
            elif status == "on_duty_not_driving":
                grid["on_duty_not_driving"].append({"start": start_minute, "end": end_minute})
        
        return grid
    
    def _calculate_totals(self, timeline: List[Dict]) -> Dict:
        totals = {
            "off_duty": 0.0,
            "sleeper_berth": 0.0,
            "driving": 0.0,
            "on_duty_not_driving": 0.0
        }
        
        for event in timeline:
            status = event["status"]
            duration = event.get("duration", 0.0)
            if status in totals:
                totals[status] += duration
        
        for key in totals:
            totals[key] = round(totals[key], 2)
        
        return totals
    
    def _generate_remarks(self, timeline: List[Dict], intermediate_cities: List[Dict] = None, day_start: datetime = None, all_intermediate_cities: List[Dict] = None, carrier_info: Dict = None) -> List[str]:
        remarks = []
        all_events_and_cities = []
        
        for event in timeline:
            event_time = event["time"]
            event_duration = event.get("duration", 0)
            event_end = event_time + timedelta(hours=event_duration)
            
            if day_start:
                day_end = day_start + timedelta(days=1)
                
                if event_time >= day_end or event_end <= day_start:
                    continue
                
                actual_start = max(event_time, day_start)
                actual_end = min(event_end, day_end)
                
                time_diff = actual_start - day_start
                hours_into_day = time_diff.total_seconds() / 3600.0
                
                if hours_into_day < 0 or hours_into_day >= 24:
                    continue
                
                event_time_for_remarks = actual_start
            else:
                hours_into_day = event_time.hour + event_time.minute / 60.0
                event_time_for_remarks = event_time
            
            all_events_and_cities.append({
                "time": event_time_for_remarks,
                "hours_into_day": hours_into_day,
                "description": event.get("description", ""),
                "location": event.get("location"),
                "type": "event"
            })
        
        if intermediate_cities:
            for city in intermediate_cities:
                hours_into_day = city.get("hours_into_day", 0)
                if hours_into_day >= 0 and hours_into_day < 24:
                    if day_start:
                        city_time = day_start + timedelta(hours=hours_into_day)
                    else:
                        city_time = datetime.now().replace(hour=int(hours_into_day), minute=int((hours_into_day - int(hours_into_day)) * 60))
                    
                    all_events_and_cities.append({
                        "time": city_time,
                        "hours_into_day": hours_into_day,
                        "description": city.get("name", ""),
                        "location": None,
                        "type": "city"
                    })
        
        all_events_and_cities.sort(key=lambda x: x["time"])
        
        for item in all_events_and_cities:
            time_str = item["time"].strftime("%I:%M %p")
            if item["type"] == "event":
                if item.get("location"):
                    remarks.append(f"{time_str} - {item['description']} - {item['location']}")
                else:
                    description = item['description']
                    if description.lower() in ['pickup', 'dropoff']:
                        location_context = ""
                        if all_intermediate_cities:
                            event_hours = item.get("hours_into_day", 0)
                            closest_city = None
                            min_diff = float('inf')
                            for city in all_intermediate_cities:
                                city_hours = city.get("hours_into_day", 0)
                                diff = abs(city_hours - event_hours)
                                if diff < min_diff and diff < 1.0:
                                    min_diff = diff
                                    closest_city = city
                            if closest_city:
                                city_name = closest_city.get("name", "")
                                city_type = closest_city.get("type", "")
                                if city_type == "pickup" and description.lower() == "pickup":
                                    location_context = f" - {city_name} area"
                                elif city_type == "dropoff" and description.lower() == "dropoff":
                                    location_context = f" - {city_name} area"
                                elif city_name:
                                    location_context = f" - {city_name} area"
                        
                        if not location_context and description.lower() == "dropoff":
                            if all_intermediate_cities:
                                dropoff_city = next((c for c in all_intermediate_cities if c.get("type") == "dropoff"), None)
                                if dropoff_city:
                                    location_context = f" - {dropoff_city.get('name', '')} area"
                            
                            if not location_context and carrier_info:
                                dropoff_location = carrier_info.get("to", "")
                                if dropoff_location:
                                    location_parts = dropoff_location.split(",")
                                    if location_parts:
                                        city_name = location_parts[0].strip()
                                        location_context = f" - {city_name} area"
                            
                            if not location_context:
                                location_context = " - dropoff area"
                        
                        remarks.append(f"{time_str} - {description}{location_context}")
                    elif "driving" in description.lower():
                        location_context = ""
                        if all_intermediate_cities:
                            event_hours = item.get("hours_into_day", 0)
                            closest_city = None
                            min_diff = float('inf')
                            for city in all_intermediate_cities:
                                city_hours = city.get("hours_into_day", 0)
                                diff = abs(city_hours - event_hours)
                                if diff < min_diff and diff < 2.0:
                                    min_diff = diff
                                    closest_city = city
                            if closest_city:
                                city_name = closest_city.get("name", "")
                                location_context = f" - {city_name} area"
                        
                        if not location_context and carrier_info:
                            dropoff_city = next((c for c in (all_intermediate_cities or []) if c.get("type") == "dropoff"), None)
                            if dropoff_city:
                                dropoff_hours = dropoff_city.get("hours_into_day", 0)
                                event_hours = item.get("hours_into_day", 0)
                                if abs(dropoff_hours - event_hours) < 2.0:
                                    location_context = f" - {dropoff_city.get('name', '')} area"
                            
                            if not location_context:
                                dropoff_location = carrier_info.get("to", "")
                                if dropoff_location:
                                    location_parts = dropoff_location.split(",")
                                    if location_parts:
                                        city_name = location_parts[0].strip()
                                        location_context = f" - {city_name} area"
                        
                        if not location_context:
                            location_context = " - route"
                        remarks.append(f"{time_str} - {description}{location_context}")
                    else:
                        remarks.append(f"{time_str} - {description}")
            else:
                city_name = item['description']
                city_type = None
                if all_intermediate_cities:
                    for city in all_intermediate_cities:
                        if city.get("name") == city_name:
                            city_type = city.get("type", "intermediate")
                            break
                
                if city_type == "pickup":
                    remarks.append(f"{time_str} - {city_name} - pickup area")
                elif city_type == "dropoff":
                    remarks.append(f"{time_str} - {city_name} - dropoff area")
                elif city_type == "start":
                    remarks.append(f"{time_str} - {city_name} - start area")
                else:
                    if "County" in city_name or "county" in city_name:
                        remarks.append(f"{time_str} - {city_name} - county area")
                    elif "Township" in city_name or "township" in city_name:
                        remarks.append(f"{time_str} - {city_name} - township area")
                    elif "City" in city_name or "city" in city_name:
                        remarks.append(f"{time_str} - {city_name} - city area")
                    else:
                        remarks.append(f"{time_str} - {city_name} - area")
        
        return remarks
    
    def _calculate_recap(self, totals: Dict, current_cycle_used: float) -> Dict:
        on_duty_today = totals.get("driving", 0.0) + totals.get("on_duty_not_driving", 0.0)
        
        total_last_7_days = current_cycle_used + on_duty_today
        available_tomorrow_70 = max(0, 70.0 - total_last_7_days)
        total_last_5_days = total_last_7_days
        
        return {
            "on_duty_today": round(on_duty_today, 2),
            "total_last_7_days": round(total_last_7_days, 2),
            "available_tomorrow_70": round(available_tomorrow_70, 2),
            "total_last_5_days": round(total_last_5_days, 2)
        }

