"""
Service modules for the Proactive Work-Life Assistant
"""
from .services.ai_service import AIService
from .services.calendar_service import CalendarService
from .location_service import LocationService
from .services.email_service import EmailService
from .restaurant_service import RestaurantService

__all__ = [
    'AIService',
    'CalendarService', 
    'LocationService',
    'EmailService',
    'RestaurantService'
] 