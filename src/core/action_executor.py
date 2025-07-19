"""
Action Executor for performing final actions
"""
from typing import Dict, Any, List, Optional
from src.services.calendar_service import CalendarService
from src.services.email_service import EmailService
from src.services.restaurant_service import RestaurantService

class ActionExecutor:
    """
    Executor that performs the final actions based on user confirmations
    """
    
    def __init__(self):
        self.calendar_service = CalendarService()
        self.email_service = EmailService()
        self.restaurant_service = RestaurantService()
    
    def execute_meeting_scheduling(self, meeting_details: Dict[str, Any], 
                                 user_email: str = None) -> Dict[str, Any]:
        """
        Execute meeting scheduling action
        
        Args:
            meeting_details: Meeting details
            user_email: User's email address
        
        Returns:
            Execution results
        """
        try:
            # Create calendar event
            event_created = self.calendar_service.create_event(meeting_details)
            
            if not event_created:
                return {
                    'success': False,
                    'message': 'Failed to create calendar event',
                    'error': 'calendar_creation_failed'
                }
            
            # Send email invites
            attendee_emails = meeting_details.get('attendees', [])
            invites_sent = False
            
            if attendee_emails:
                invites_sent = self.email_service.send_meeting_invite(
                    meeting_details, attendee_emails, user_email or 'assistant@company.com'
                )
            
            return {
                'success': True,
                'message': f'Meeting scheduled successfully! Event created and invites sent to {len(attendee_emails)} attendees.',
                'event_created': event_created,
                'invites_sent': invites_sent,
                'attendee_count': len(attendee_emails)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error scheduling meeting: {str(e)}',
                'error': str(e)
            }
    
    def execute_restaurant_booking(self, restaurant_details: Dict[str, Any],
                                 user_email: str = None) -> Dict[str, Any]:
        """
        Execute restaurant booking action
        
        Args:
            restaurant_details: Restaurant booking details
            user_email: User's email address
        
        Returns:
            Execution results
        """
        try:
            # For demo purposes, simulate booking
            # In a real implementation, you'd integrate with restaurant booking APIs
            restaurant_name = restaurant_details.get('name', 'Restaurant')
            
            # Send dinner invites
            attendee_emails = restaurant_details.get('attendees', [])
            invites_sent = False
            
            if attendee_emails:
                invites_sent = self.email_service.send_dinner_invite(
                    restaurant_details, attendee_emails, user_email or 'assistant@company.com'
                )
            
            return {
                'success': True,
                'message': f'Restaurant booking confirmed at {restaurant_name}! Invites sent to {len(attendee_emails)} attendees.',
                'booking_confirmed': True,
                'invites_sent': invites_sent,
                'attendee_count': len(attendee_emails)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error booking restaurant: {str(e)}',
                'error': str(e)
            }
    
    def execute_availability_check(self, availability_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute availability checking action
        
        Args:
            availability_details: Availability check details
        
        Returns:
            Execution results
        """
        try:
            employee_emails = availability_details.get('employees', [])
            target_date = availability_details.get('date')
            
            if not target_date or not employee_emails:
                return {
                    'success': False,
                    'message': 'Missing required information for availability check',
                    'error': 'missing_required_fields'
                }
            
            # Get schedules for all employees
            schedules = {}
            for email in employee_emails:
                schedule = self.calendar_service.get_user_schedule(
                    email, target_date, target_date
                )
                schedules[email] = schedule
            
            return {
                'success': True,
                'message': f'Availability checked for {len(employee_emails)} team members.',
                'schedules': schedules,
                'target_date': target_date,
                'employee_count': len(employee_emails)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error checking availability: {str(e)}',
                'error': str(e)
            }
    
    def execute_action(self, action_type: str, action_details: Dict[str, Any],
                      user_email: str = None) -> Dict[str, Any]:
        """
        Execute an action based on type
        
        Args:
            action_type: Type of action to execute
            action_details: Action details
            user_email: User's email address
        
        Returns:
            Execution results
        """
        if action_type == 'meeting_scheduling':
            return self.execute_meeting_scheduling(action_details, user_email)
        elif action_type == 'restaurant_booking':
            return self.execute_restaurant_booking(action_details, user_email)
        elif action_type == 'availability_check':
            return self.execute_availability_check(action_details)
        else:
            return {
                'success': False,
                'message': f'Unknown action type: {action_type}',
                'error': 'unknown_action_type'
            } 