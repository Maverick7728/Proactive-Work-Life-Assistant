"""
Service modules for the Proactive Work-Life Assistant
"""
from .ai_service import AIService
from .calendar_service import CalendarService
from .location_service import LocationService
from .email_service import EmailService
from .restaurant_service import RestaurantService

__all__ = [
    'AIService',
    'CalendarService', 
    'LocationService',
    'EmailService',
    'RestaurantService'
] 