from datetime import datetime, timedelta
from typing import List, Dict, Optional
from decimal import Decimal, ROUND_HALF_UP


class LogGenerator:
    MINUTES_PER_DAY = 24 * 60
    
    def generate_log_sheets(
        self,
        timeline: List[Dict],
        start_time: datetime,
        total_miles: float,
        carrier_info: Dict,
        vehicle_info: Dict
    ) -> List[Dict]:
        log_sheets = []
        current_date = start_time.date()
        end_time = timeline[-1]["time"] + timedelta(hours=timeline[-1].get("duration", 0))
        
        current_sheet_start = start_time
        day_index = 0
        
        while current_sheet_start < end_time:
            sheet_end = min(
                current_sheet_start + timedelta(days=1),
                end_time
            )
            
            sheet_timeline = [
                event for event in timeline
                if current_sheet_start <= event["time"] < sheet_end
            ]
            
            if not sheet_timeline and current_sheet_start < end_time:
                sheet_timeline = [{
                    "time": current_sheet_start,
                    "status": "off_duty",
                    "description": "Off duty",
                    "duration": (sheet_end - current_sheet_start).total_seconds() / 3600.0,
                    "location": None
                }]
            
            log_sheet = self._generate_single_log_sheet(
                sheet_timeline,
                current_sheet_start,
                sheet_end,
                total_miles if day_index == 0 else 0.0,
                carrier_info,
                vehicle_info,
                day_index
            )
            
            log_sheets.append(log_sheet)
            current_sheet_start = sheet_end
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
        day_index: int
    ) -> Dict:
        grid = self._generate_grid(timeline, start_time)
        totals = self._calculate_totals(timeline)
        remarks = self._generate_remarks(timeline)
        
        return {
            "date": start_time.strftime("%m/%d/%Y"),
            "from": carrier_info.get("from", ""),
            "to": carrier_info.get("to", ""),
            "total_miles_driving": round(total_miles, 1),
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
            "recap": self._calculate_recap(totals, carrier_info.get("current_cycle_used", 0))
        }
    
    def _generate_grid(
        self,
        timeline: List[Dict],
        start_time: datetime
    ) -> Dict:
        grid = {
            "off_duty": [],
            "sleeper_berth": [],
            "driving": [],
            "on_duty_not_driving": []
        }
        
        current_minute = 0
        
        for event in timeline:
            event_start = event["time"]
            event_duration_minutes = int(event.get("duration", 0) * 60)
            
            start_minute = int((event_start - start_time).total_seconds() / 60)
            end_minute = min(start_minute + event_duration_minutes, self.MINUTES_PER_DAY)
            
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
    
    def _generate_remarks(self, timeline: List[Dict]) -> List[str]:
        remarks = []
        for event in timeline:
            if event.get("location"):
                location = event["location"]
                time_str = event["time"].strftime("%I:%M %p")
                remarks.append(f"{time_str} - {event['description']} - {location}")
            else:
                time_str = event["time"].strftime("%I:%M %p")
                remarks.append(f"{time_str} - {event['description']}")
        
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

