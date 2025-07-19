"""
Validation utilities for the Proactive Work-Life Assistant
"""
import re
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from config.settings import DATE_FORMATS, TIME_FORMATS, TEAM_SIZE_LIMIT

def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_date(date_str: str) -> bool:
    """
    Validate date format
    
    Args:
        date_str: Date string to validate
    
    Returns:
        True if valid, False otherwise
    """
    for fmt in DATE_FORMATS:
        try:
            datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            continue
    return False

def validate_time(time_str: str) -> bool:
    """
    Validate time format
    
    Args:
        time_str: Time string to validate
    
    Returns:
        True if valid, False otherwise
    """
    for fmt in TIME_FORMATS:
        try:
            datetime.strptime(time_str, fmt)
            return True
        except ValueError:
            continue
    return False

def validate_team_size(size: int) -> bool:
    """
    Validate team size
    
    Args:
        size: Team size to validate
    
    Returns:
        True if valid, False otherwise
    """
    return 1 <= size <= TEAM_SIZE_LIMIT

def validate_meeting_duration(duration: int) -> bool:
    """
    Validate meeting duration
    
    Args:
        duration: Duration in minutes
    
    Returns:
        True if valid, False otherwise
    """
    return 15 <= duration <= 480  # 15 minutes to 8 hours

def validate_location(location: str) -> bool:
    """
    Validate location string
    
    Args:
        location: Location string to validate
    
    Returns:
        True if valid, False otherwise
    """
    return len(location.strip()) > 0 and len(location) <= 200

def validate_employee_names(names: List[str]) -> bool:
    """
    Validate employee names
    
    Args:
        names: List of employee names
    
    Returns:
        True if valid, False otherwise
    """
    if not names:
        return False
    
    for name in names:
        if not name or len(name.strip()) == 0 or len(name) > 50:
            return False
    
    return True

def validate_meeting_details(details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate meeting details
    
    Args:
        details: Meeting details dictionary
    
    Returns:
        Dictionary with validation results
    """
    errors = []
    
    # Required fields
    required_fields = ['title', 'date', 'time', 'attendees']
    for field in required_fields:
        if field not in details or not details[field]:
            errors.append(f"Missing required field: {field}")
    
    # Validate date
    if 'date' in details and not validate_date(details['date']):
        errors.append("Invalid date format")
    
    # Validate time
    if 'time' in details and not validate_time(details['time']):
        errors.append("Invalid time format")
    
    # Validate attendees
    if 'attendees' in details:
        if not isinstance(details['attendees'], list):
            errors.append("Attendees must be a list")
        elif not validate_employee_names(details['attendees']):
            errors.append("Invalid attendee names")
    
    # Validate duration
    if 'duration' in details and not validate_meeting_duration(details['duration']):
        errors.append("Invalid meeting duration")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def validate_restaurant_details(details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate restaurant details
    
    Args:
        details: Restaurant details dictionary
    
    Returns:
        Dictionary with validation results
    """
    errors = []
    
    # Required fields
    required_fields = ['name', 'location']
    for field in required_fields:
        if field not in details or not details[field]:
            errors.append(f"Missing required field: {field}")
    
    # Validate location
    if 'location' in details and not validate_location(details['location']):
        errors.append("Invalid location")
    
    # Validate rating if present
    if 'rating' in details:
        rating = details['rating']
        if not isinstance(rating, (int, float)) or rating < 0 or rating > 5:
            errors.append("Rating must be between 0 and 5")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def sanitize_input(text: str) -> str:
    """
    Sanitize user input
    
    Args:
        text: Input text to sanitize
    
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', text)
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    return sanitized

def validate_api_response(response: Dict[str, Any]) -> bool:
    """
    Validate API response
    
    Args:
        response: API response dictionary
    
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(response, dict):
        return False
    
    # Check for common error indicators
    error_keys = ['error', 'errors', 'message', 'status']
    for key in error_keys:
        if key in response and response[key]:
            return False
    
    return True 