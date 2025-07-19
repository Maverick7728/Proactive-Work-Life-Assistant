"""
Formatting utilities for the Proactive Work-Life Assistant
"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import json

def format_date(date_obj: date, format_str: str = "%B %d, %Y") -> str:
    """
    Format date object to string
    
    Args:
        date_obj: Date object to format
        format_str: Format string
    
    Returns:
        Formatted date string
    """
    if isinstance(date_obj, str):
        # Try to parse the string date
        for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]:
            try:
                date_obj = datetime.strptime(date_obj, fmt).date()
                break
            except ValueError:
                continue
    
    if isinstance(date_obj, date):
        return date_obj.strftime(format_str)
    
    return str(date_obj)

def format_time(time_obj: datetime, format_str: str = "%I:%M %p") -> str:
    """
    Format time object to string
    
    Args:
        time_obj: Time object to format
        format_str: Format string
    
    Returns:
        Formatted time string
    """
    if isinstance(time_obj, str):
        # Try to parse the string time
        for fmt in ["%H:%M", "%I:%M %p", "%I:%M%p"]:
            try:
                time_obj = datetime.strptime(time_obj, fmt)
                break
            except ValueError:
                continue
    
    if isinstance(time_obj, datetime):
        return time_obj.strftime(format_str)
    
    return str(time_obj)

def format_duration(minutes: int) -> str:
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

def format_attendees(attendees: List[str]) -> str:
    """
    Format attendees list to string
    
    Args:
        attendees: List of attendee names
    
    Returns:
        Formatted attendees string
    """
    if not attendees:
        return "No attendees"
    
    if len(attendees) == 1:
        return attendees[0]
    elif len(attendees) == 2:
        return f"{attendees[0]} and {attendees[1]}"
    else:
        return f"{', '.join(attendees[:-1])}, and {attendees[-1]}"

def format_meeting_details(details: Dict[str, Any]) -> str:
    """
    Format meeting details for display
    
    Args:
        details: Meeting details dictionary
    
    Returns:
        Formatted meeting details string
    """
    lines = []
    
    if 'title' in details:
        lines.append(f"**Title:** {details['title']}")
    
    if 'date' in details:
        formatted_date = format_date(details['date'])
        lines.append(f"**Date:** {formatted_date}")
    
    if 'time' in details:
        formatted_time = format_time(details['time'])
        lines.append(f"**Time:** {formatted_time}")
    
    if 'duration' in details:
        formatted_duration = format_duration(details['duration'])
        lines.append(f"**Duration:** {formatted_duration}")
    
    if 'location' in details:
        lines.append(f"**Location:** {details['location']}")
    
    if 'attendees' in details:
        formatted_attendees = format_attendees(details['attendees'])
        lines.append(f"**Attendees:** {formatted_attendees}")
    
    return "\n".join(lines)

def format_restaurant_details(details: Dict[str, Any]) -> str:
    """
    Format restaurant details for display
    
    Args:
        details: Restaurant details dictionary
    
    Returns:
        Formatted restaurant details string
    """
    lines = []
    
    if 'name' in details:
        lines.append(f"**Name:** {details['name']}")
    
    if 'address' in details:
        lines.append(f"**Address:** {details['address']}")
    
    if 'cuisine' in details:
        lines.append(f"**Cuisine:** {details['cuisine']}")
    
    if 'rating' in details:
        lines.append(f"**Rating:** {details['rating']}/5")
    
    if 'distance' in details:
        lines.append(f"**Distance:** {details['distance']} km")
    
    if 'price_range' in details:
        lines.append(f"**Price Range:** {details['price_range']}")
    
    return "\n".join(lines)

def format_time_slots(time_slots: List[Dict[str, Any]]) -> str:
    """
    Format time slots for display
    
    Args:
        time_slots: List of time slot dictionaries
    
    Returns:
        Formatted time slots string
    """
    if not time_slots:
        return "No available time slots found."
    
    lines = ["Available time slots:"]
    
    for i, slot in enumerate(time_slots, 1):
        start_time = format_time(slot.get('start_time', ''))
        end_time = format_time(slot.get('end_time', ''))
        lines.append(f"{i}. {start_time} - {end_time}")
    
    return "\n".join(lines)

def format_restaurant_options(restaurants: List[Dict[str, Any]]) -> str:
    """
    Format restaurant options for display
    
    Args:
        restaurants: List of restaurant dictionaries
    
    Returns:
        Formatted restaurant options string
    """
    if not restaurants:
        return "No restaurants found matching your criteria."
    
    lines = ["Restaurant options:"]
    
    for i, restaurant in enumerate(restaurants, 1):
        lines.append(f"\n**Option {i}:**")
        lines.append(format_restaurant_details(restaurant))
    
    return "\n".join(lines)

def format_confirmation_message(action_type: str, action_details: Dict[str, Any]) -> str:
    """
    Format confirmation message for user
    
    Args:
        action_type: Type of action to confirm
        action_details: Details of the action
    
    Returns:
        Formatted confirmation message
    """
    if action_type == "meeting_scheduling":
        title = action_details.get('title', 'Meeting')
        date = action_details.get('date', 'TBD')
        time = action_details.get('time', 'TBD')
        duration = action_details.get('duration', 60)
        attendees = action_details.get('attendees', [])
        
        return f"""
Please confirm the following meeting details:

📅 **Meeting:** {title}
📆 **Date:** {date}
⏰ **Time:** {time}
⏱️ **Duration:** {format_duration(duration)}
👥 **Attendees:** {', '.join(attendees) if attendees else 'TBD'}

Do you want to proceed with scheduling this meeting?
        """.strip()
    
    elif action_type == "restaurant_booking":
        name = action_details.get('name', 'Restaurant')
        date = action_details.get('date', 'TBD')
        time = action_details.get('time', 'TBD')
        address = action_details.get('address', 'TBD')
        cuisine = action_details.get('cuisine', 'Various')
        attendees = action_details.get('attendees', [])
        
        return f"""
Please confirm the following restaurant booking:

🍽️ **Restaurant:** {name}
📆 **Date:** {date}
⏰ **Time:** {time}
📍 **Address:** {address}
🍴 **Cuisine:** {cuisine}
👥 **Attendees:** {', '.join(attendees) if attendees else 'TBD'}

Do you want to proceed with this booking?
        """.strip()
    
    else:
        return f"""
Please confirm the following action:

**Action Type:** {action_type}
**Details:** {json.dumps(action_details, indent=2)}

Do you want to proceed?
        """.strip()

def format_error_message(message: str) -> str:
    """
    Format error message
    
    Args:
        message: Error message
    
    Returns:
        Formatted error message
    """
    return f"❌ {message}"

def format_success_message(message: str) -> str:
    """
    Format success message
    
    Args:
        message: Success message
    
    Returns:
        Formatted success message
    """
    return f"✅ {message}"

def format_warning_message(message: str) -> str:
    """
    Format warning message
    
    Args:
        message: Warning message
    
    Returns:
        Formatted warning message
    """
    return f"⚠️ {message}"

def format_info_message(message: str) -> str:
    """
    Format info message
    
    Args:
        message: Info message
    
    Returns:
        Formatted info message
    """
    return f"ℹ️ {message}"

def format_list(items: List[str], bullet: str = "•") -> str:
    """
    Format list of items with bullets
    
    Args:
        items: List of items
        bullet: Bullet character
    
    Returns:
        Formatted list string
    """
    return "\n".join([f"{bullet} {item}" for item in items])

def format_table(data: List[Dict[str, Any]], headers: List[str] = None) -> str:
    """
    Format data as a table string
    
    Args:
        data: List of dictionaries
        headers: Column headers (optional)
    
    Returns:
        Formatted table string
    """
    if not data:
        return "No data available"
    
    if headers is None:
        headers = list(data[0].keys())
    
    # Calculate column widths
    col_widths = {}
    for header in headers:
        col_widths[header] = len(header)
    
    for row in data:
        for header in headers:
            value = str(row.get(header, ''))
            col_widths[header] = max(col_widths[header], len(value))
    
    # Create table
    table_lines = []
    
    # Header
    header_line = "| " + " | ".join(header.ljust(col_widths[header]) for header in headers) + " |"
    table_lines.append(header_line)
    
    # Separator
    separator_line = "|" + "|".join("-" * (col_widths[header] + 2) for header in headers) + "|"
    table_lines.append(separator_line)
    
    # Data rows
    for row in data:
        row_line = "| " + " | ".join(str(row.get(header, '')).ljust(col_widths[header]) for header in headers) + " |"
        table_lines.append(row_line)
    
    return "\n".join(table_lines)

def format_json(data: Dict[str, Any], indent: int = 2) -> str:
    """
    Format data as JSON string
    
    Args:
        data: Data to format
        indent: Indentation level
    
    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=indent, default=str)

def format_phone_number(phone: str) -> str:
    """
    Format phone number for display
    
    Args:
        phone: Phone number string
    
    Returns:
        Formatted phone number
    """
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        return phone  # Return original if can't format

def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format currency amount
    
    Args:
        amount: Amount to format
        currency: Currency code
    
    Returns:
        Formatted currency string
    """
    if currency == "USD":
        return f"${amount:.2f}"
    elif currency == "EUR":
        return f"€{amount:.2f}"
    elif currency == "INR":
        return f"₹{amount:.2f}"
    else:
        return f"{amount:.2f} {currency}"

def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format percentage value
    
    Args:
        value: Value to format (0-1)
        decimal_places: Number of decimal places
    
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimal_places}f}%"

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human readable string
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted file size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB" 