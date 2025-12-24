from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum


class DutyStatus(Enum):
    OFF_DUTY = "off_duty"
    SLEEPER_BERTH = "sleeper_berth"
    DRIVING = "driving"
    ON_DUTY_NOT_DRIVING = "on_duty_not_driving"


class HOSCalculator:
    MAX_70_HOUR_LIMIT = 70.0
    MAX_14_HOUR_WINDOW = 14.0
    MAX_11_HOUR_DRIVING = 11.0
    MIN_10_HOUR_REST = 10.0
    MIN_30_MIN_BREAK = 0.5
    BREAK_AFTER_HOURS = 8.0
    AVERAGE_SPEED_MPH = 60.0
    FUEL_STOP_DURATION = 0.5
    
    def __init__(self, current_cycle_used: float, start_time: datetime):
        self.current_cycle_used = current_cycle_used
        self.start_time = start_time
        self.available_70_hour_hours = self.MAX_70_HOUR_LIMIT - current_cycle_used
    
    def calculate_trip_timeline(
        self,
        total_distance_miles: float,
        pickup_duration: float = 1.0,
        dropoff_duration: float = 1.0
    ) -> Dict:
        timeline = []
        current_time = self.start_time
        total_driving_hours = total_distance_miles / self.AVERAGE_SPEED_MPH
        
        timeline.append({
            "time": current_time,
            "status": DutyStatus.ON_DUTY_NOT_DRIVING.value,
            "description": "Pickup",
            "duration": pickup_duration,
            "location": None
        })
        current_time += timedelta(hours=pickup_duration)
        
        driving_segments = self._calculate_driving_segments(
            total_driving_hours,
            current_time
        )
        
        timeline.extend(driving_segments)
        
        if timeline:
            last_event = timeline[-1]
            current_time = last_event["time"] + timedelta(hours=last_event.get("duration", 0))
        
        timeline.append({
            "time": current_time,
            "status": DutyStatus.ON_DUTY_NOT_DRIVING.value,
            "description": "Dropoff",
            "duration": dropoff_duration,
            "location": None
        })
        
        return {
            "timeline": timeline,
            "total_driving_hours": total_driving_hours,
            "total_on_duty_hours": self._calculate_total_on_duty(timeline),
            "compliance": self._check_compliance(timeline)
        }
    
    def _calculate_driving_segments(
        self,
        total_driving_hours: float,
        start_time: datetime
    ) -> List[Dict]:
        segments = []
        current_time = start_time
        remaining_driving = total_driving_hours
        cumulative_driving_since_break = 0.0
        window_start = start_time
        window_driving_hours = 0.0
        
        while remaining_driving > 0:
            window_elapsed = (current_time - window_start).total_seconds() / 3600.0
            window_remaining = self.MAX_14_HOUR_WINDOW - window_elapsed
            
            driving_available_in_window = min(
                self.MAX_11_HOUR_DRIVING - window_driving_hours,
                remaining_driving
            )
            
            if window_remaining <= 0.01 or driving_available_in_window <= 0.01:
                segments.append({
                    "time": current_time,
                    "status": DutyStatus.SLEEPER_BERTH.value,
                    "description": "10-hour rest break (sleeper berth)",
                    "duration": self.MIN_10_HOUR_REST,
                    "location": None
                })
                current_time += timedelta(hours=self.MIN_10_HOUR_REST)
                window_start = current_time
                window_driving_hours = 0.0
                cumulative_driving_since_break = 0.0
                continue
            
            driving_before_break_needed = self.BREAK_AFTER_HOURS - cumulative_driving_since_break
            segment_driving = min(
                driving_available_in_window,
                window_remaining,
                remaining_driving,
                driving_before_break_needed if driving_before_break_needed > 0 else float('inf')
            )
            
            if segment_driving <= 0:
                break
            
            if cumulative_driving_since_break + segment_driving >= self.BREAK_AFTER_HOURS:
                driving_to_break = self.BREAK_AFTER_HOURS - cumulative_driving_since_break
                
                if driving_to_break > 0.01:
                    segments.append({
                        "time": current_time,
                        "status": DutyStatus.DRIVING.value,
                        "description": "Driving",
                        "duration": driving_to_break,
                        "location": None
                    })
                    current_time += timedelta(hours=driving_to_break)
                    cumulative_driving_since_break += driving_to_break
                    window_driving_hours += driving_to_break
                    remaining_driving -= driving_to_break
                
                segments.append({
                    "time": current_time,
                    "status": DutyStatus.OFF_DUTY.value,
                    "description": "30-minute break",
                    "duration": self.MIN_30_MIN_BREAK,
                    "location": None
                })
                current_time += timedelta(hours=self.MIN_30_MIN_BREAK)
                cumulative_driving_since_break = 0.0
            else:
                segments.append({
                    "time": current_time,
                    "status": DutyStatus.DRIVING.value,
                    "description": "Driving",
                    "duration": segment_driving,
                    "location": None
                })
                current_time += timedelta(hours=segment_driving)
                cumulative_driving_since_break += segment_driving
                window_driving_hours += segment_driving
                remaining_driving -= segment_driving
        
        return segments
    
    def _calculate_total_on_duty(self, timeline: List[Dict]) -> float:
        total = 0.0
        for event in timeline:
            if event["status"] in [DutyStatus.DRIVING.value, DutyStatus.ON_DUTY_NOT_DRIVING.value]:
                total += event.get("duration", 0.0)
        return total
    
    def _check_compliance(self, timeline: List[Dict]) -> Dict:
        total_on_duty = self._calculate_total_on_duty(timeline)
        required_70_hour_hours = self.current_cycle_used + total_on_duty
        
        return {
            "compliant": required_70_hour_hours <= self.MAX_70_HOUR_LIMIT,
            "total_on_duty": total_on_duty,
            "required_70_hour_hours": required_70_hour_hours,
            "available_hours": self.available_70_hour_hours,
            "exceeds_by": max(0, required_70_hour_hours - self.MAX_70_HOUR_LIMIT)
        }

