"""
Time formatting utilities for the Proactive Work-Life Assistant
"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import pytz
from config.settings import DEFAULT_TIMEZONE, WORKING_HOURS

class TimeFormatter:
    """
    Utility class for time formatting and manipulation
    """
    
    def __init__(self, timezone: str = DEFAULT_TIMEZONE):
        self.timezone = pytz.timezone(timezone)
        self.working_hours = WORKING_HOURS
    
    def parse_date(self, date_str: str) -> Optional[date]:
        """
        Parse date string to date object
        
        Args:
            date_str: Date string to parse
        
        Returns:
            Date object or None if parsing fails
        """
        from config.settings import DATE_FORMATS
        
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        # Fallback: try dateutil.parser.parse for natural language dates
        try:
            from dateutil.parser import parse as dateutil_parse
            return dateutil_parse(date_str, fuzzy=True).date()
        except Exception:
            return None
    
    def parse_time(self, time_str: str) -> Optional[datetime]:
        """
        Parse time string to datetime object
        
        Args:
            time_str: Time string to parse
        
        Returns:
            Datetime object or None if parsing fails
        """
        from config.settings import TIME_FORMATS
        
        for fmt in TIME_FORMATS:
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def format_date(self, date_obj: date, format_str: str = "%B %d, %Y") -> str:
        """
        Format date object to string
        
        Args:
            date_obj: Date object to format
            format_str: Format string
        
        Returns:
            Formatted date string
        """
        if isinstance(date_obj, str):
            parsed = self.parse_date(date_obj)
            if parsed:
                date_obj = parsed
        
        if isinstance(date_obj, date):
            return date_obj.strftime(format_str)
        
        return str(date_obj)
    
    def format_time(self, time_obj: datetime, format_str: str = "%I:%M %p") -> str:
        """
        Format time object to string
        
        Args:
            time_obj: Time object to format
            format_str: Format string
        
        Returns:
            Formatted time string
        """
        if isinstance(time_obj, str):
            parsed = self.parse_time(time_obj)
            if parsed:
                time_obj = parsed
        
        if isinstance(time_obj, datetime):
            return time_obj.strftime(format_str)
        
        return str(time_obj)
    
    def get_working_hours(self, target_date: date) -> List[Dict[str, str]]:
        """
        Get working hours for a specific date
        
        Args:
            target_date: Target date
        
        Returns:
            List of working hour slots
        """
        slots = []
        
        # Parse working hours
        start_time = datetime.strptime(self.working_hours['start'], "%H:%M")
        end_time = datetime.strptime(self.working_hours['end'], "%H:%M")
        
        # Create time slots (1-hour intervals)
        current_time = start_time
        while current_time < end_time:
            slot_end = current_time + timedelta(hours=1)
            if slot_end > end_time:
                slot_end = end_time
            
            slots.append({
                'start_time': current_time.strftime("%H:%M"),
                'end_time': slot_end.strftime("%H:%M")
            })
            
            current_time = slot_end
        
        return slots
    
    def is_working_hour(self, time_obj: datetime) -> bool:
        """
        Check if time is within working hours
        
        Args:
            time_obj: Time to check
        
        Returns:
            True if within working hours, False otherwise
        """
        time_str = time_obj.strftime("%H:%M")
        start_time = self.working_hours['start']
        end_time = self.working_hours['end']
        
        return start_time <= time_str <= end_time
    
    def get_next_working_day(self, from_date: date = None) -> date:
        """
        Get the next working day
        
        Args:
            from_date: Starting date (defaults to today)
        
        Returns:
            Next working day
        """
        if from_date is None:
            from_date = date.today()
        
        current_date = from_date
        while True:
            current_date += timedelta(days=1)
            # Skip weekends (Saturday=5, Sunday=6)
            if current_date.weekday() < 5:
                return current_date
    
    def get_week_range(self, target_date: date) -> Dict[str, date]:
        """
        Get the week range for a given date
        
        Args:
            target_date: Target date
        
        Returns:
            Dictionary with start and end of week
        """
        # Get Monday of the week
        days_since_monday = target_date.weekday()
        monday = target_date - timedelta(days=days_since_monday)
        
        # Get Sunday of the week
        sunday = monday + timedelta(days=6)
        
        return {
            'start': monday,
            'end': sunday
        }
    
    def get_month_range(self, target_date: date) -> Dict[str, date]:
        """
        Get the month range for a given date
        
        Args:
            target_date: Target date
        
        Returns:
            Dictionary with start and end of month
        """
        # First day of month
        start = target_date.replace(day=1)
        
        # Last day of month
        if target_date.month == 12:
            end = target_date.replace(year=target_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = target_date.replace(month=target_date.month + 1, day=1) - timedelta(days=1)
        
        return {
            'start': start,
            'end': end
        }
    
    def add_duration(self, start_time: datetime, duration_minutes: int) -> datetime:
        """
        Add duration to start time
        
        Args:
            start_time: Start time
            duration_minutes: Duration in minutes
        
        Returns:
            End time
        """
        return start_time + timedelta(minutes=duration_minutes)
    
    def get_time_slots(self, start_time: str, end_time: str, duration_minutes: int = 60) -> List[Dict[str, str]]:
        """
        Generate time slots between start and end time
        
        Args:
            start_time: Start time string
            end_time: End time string
            duration_minutes: Duration of each slot in minutes
        
        Returns:
            List of time slot dictionaries
        """
        slots = []
        
        start = self.parse_time(start_time)
        end = self.parse_time(end_time)
        
        if not start or not end:
            return slots
        
        current = start
        while current < end:
            slot_end = self.add_duration(current, duration_minutes)
            if slot_end > end:
                slot_end = end
            
            slots.append({
                'start_time': self.format_time(current),
                'end_time': self.format_time(slot_end)
            })
            
            current = slot_end
        
        return slots
    
    def is_weekend(self, target_date: date) -> bool:
        """
        Check if date is a weekend
        
        Args:
            target_date: Date to check
        
        Returns:
            True if weekend, False otherwise
        """
        return target_date.weekday() >= 5
    
    def get_relative_date(self, relative_str: str) -> Optional[date]:
        """
        Parse relative date strings like "tomorrow", "next week", etc.
        
        Args:
            relative_str: Relative date string
        
        Returns:
            Date object or None if parsing fails
        """
        today = date.today()
        relative_str = relative_str.lower().strip()
        
        if relative_str == "today":
            return today
        elif relative_str == "tomorrow":
            return today + timedelta(days=1)
        elif relative_str == "yesterday":
            return today - timedelta(days=1)
        elif relative_str == "next week":
            return self.get_next_working_day(today)
        elif relative_str == "next monday":
            days_until_monday = (7 - today.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            return today + timedelta(days=days_until_monday)
        elif relative_str == "next friday":
            days_until_friday = (4 - today.weekday()) % 7
            if days_until_friday == 0:
                days_until_friday = 7
            return today + timedelta(days=days_until_friday)
        
        return None
    
    def format_duration(self, minutes: int) -> str:
        """
        Format duration in minutes to human readable string
        
        Args:
            minutes: Duration in minutes
        
        Returns:
            Formatted duration string
        """
        if minutes < 60:
            return f"{minutes} minutes"
        elif minutes == 60:
            return "1 hour"
        else:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            if remaining_minutes == 0:
                return f"{hours} hours"
            else:
                return f"{hours} hours {remaining_minutes} minutes"
    
    def get_timezone_aware_datetime(self, dt: datetime) -> datetime:
        """
        Make datetime timezone aware
        
        Args:
            dt: Datetime object
        
        Returns:
            Timezone aware datetime
        """
        if dt.tzinfo is None:
            return self.timezone.localize(dt)
        return dt
    
    def convert_timezone(self, dt: datetime, target_timezone: str) -> datetime:
        """
        Convert datetime to different timezone
        
        Args:
            dt: Datetime object
            target_timezone: Target timezone string
        
        Returns:
            Converted datetime
        """
        target_tz = pytz.timezone(target_timezone)
        
        if dt.tzinfo is None:
            dt = self.timezone.localize(dt)
        
        return dt.astimezone(target_tz) 