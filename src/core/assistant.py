"""
Main Assistant Coordinator for the Proactive Work-Life Assistant
"""
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from pathlib import Path
from .goal_parser import GoalParser
from .task_planner import TaskPlanner
from .action_executor import ActionExecutor
from .user_manager import UserManager
from src.utils.name_matcher import NameMatcher
from .confirmation_handler import ConfirmationHandler
from src.services.ai_service import AIService
from src.services.calendar_service import CalendarService
from src.services.email_service import EmailService
from src.services.location_service import LocationService
from src.services.restaurant_service import RestaurantService
from src.utils.logger import setup_logger
from src.utils.formatters import format_success_message, format_error_message
import json

class Assistant:
    """
    Main assistant coordinator that orchestrates all operations
    """
    
    def __init__(self):
        # Initialize logger
        self.logger = setup_logger("assistant")
        
        # Ensure data directories exist
        self._ensure_data_directories()
        
        # Initialize core components
        self.goal_parser = GoalParser()
        self.task_planner = TaskPlanner()
        self.action_executor = ActionExecutor()
        self.user_manager = UserManager()
        self.name_matcher = NameMatcher()  # Use enhanced NameMatcher instead of EmployeeFilter
        self.confirmation_handler = ConfirmationHandler()
        
        # Initialize services
        self.ai_service = AIService()
        self.calendar_service = CalendarService()
        self.email_service = EmailService()
        self.location_service = LocationService()
        self.restaurant_service = RestaurantService()
        
        # Initialize state
        self.current_session = None
        self.conversation_history = []
        
        self.logger.info("Assistant initialized successfully")
    
    def _ensure_data_directories(self):
        """Ensure all required data directories exist"""
        try:
            # Get base directory
            base_dir = Path(__file__).parent.parent.parent
            
            # Create data directories
            data_dirs = [
                base_dir / "data",
                base_dir / "data" / "users",
                base_dir / "data" / "calendar",
                base_dir / "data" / "emails",
                base_dir / "data" / "restaurants"
            ]
            
            for dir_path in data_dirs:
                dir_path.mkdir(parents=True, exist_ok=True)
                
            self.logger.info("Data directories ensured")
            
        except Exception as e:
            self.logger.error(f"Error creating data directories: {e}")
    
    def _convert_date_string_to_date(self, date_str: str) -> Optional[date]:
        """
        Convert date string to date object
        
        Args:
            date_str: Date string (ISO format or natural language)
        
        Returns:
            Date object or None if conversion fails
        """
        if isinstance(date_str, date):
            return date_str
        elif isinstance(date_str, datetime):
            return date_str.date()
        elif isinstance(date_str, str):
            # Try to parse using time formatter
            # parsed_date = self.time_formatter.parse_date(date_str) # This line was removed as per the new_code
            # if parsed_date:
            #     return parsed_date
            # If that fails, try dateutil
            try:
                from dateutil.parser import parse as dateutil_parse
                return dateutil_parse(date_str, fuzzy=True).date()
            except Exception:
                self.logger.error(f"Could not parse date: {date_str}")
                return None
        return None
    
    def process_user_query(self, user_query: str, user_email: str = None) -> Dict[str, Any]:
        """
        Process a user query and return a response
        
        Args:
            user_query: User's natural language query
            user_email: User's email address (optional)
        
        Returns:
            Dictionary with response and next actions
        """
        try:
            self.logger.info(f"Processing user query: {user_query}")
            
            # Add to conversation history
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'user_query': user_query,
                'user_email': user_email
            })
            
            # Step 1: Parse the goal
            goal_info = self.goal_parser.parse_goal(user_query)
            
            if not goal_info:
                return {
                    'success': False,
                    'message': "I couldn't understand your request. Could you please rephrase it?",
                    'next_action': 'clarify'
                }
            
            # Step 2: Extract employee names if mentioned
            if goal_info.get('type') in ['meeting', 'dinner']:
                employee_names = self.name_matcher.extract_employee_names(user_query)
                if employee_names:
                    goal_info['employees'] = employee_names
                    goal_info['employee_emails'] = self.name_matcher.get_emails_for_names(employee_names)
            
            # Step 3: Plan the task
            task_plan = self.task_planner.create_plan(goal_info)
            
            if not task_plan:
                return {
                    'success': False,
                    'message': "I couldn't create a plan for your request. Please provide more details.",
                    'next_action': 'clarify'
                }
            
            # Step 4: Execute the plan
            result = self._execute_plan(task_plan, user_email)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing user query: {e}")
            return {
                'success': False,
                'message': format_error_message(f"An error occurred: {str(e)}"),
                'next_action': 'error'
            }
    
    def _execute_plan(self, task_plan: Dict[str, Any], user_email: str = None) -> Dict[str, Any]:
        """
        Execute a task plan
        
        Args:
            task_plan: Task plan to execute
            user_email: User's email address
        
        Returns:
            Dictionary with execution results
        """
        try:
            task_type = task_plan.get('type')
            
            if task_type == 'meeting_scheduling':
                return self._handle_meeting_scheduling(task_plan, user_email)
            elif task_type == 'restaurant_booking':
                return self._handle_restaurant_booking(task_plan, user_email)
            elif task_type == 'availability_check':
                return self._handle_availability_check(task_plan, user_email)
            elif task_type == 'send_email':
                return self._handle_send_email(task_plan, user_email)
            else:
                return {
                    'success': False,
                    'message': f"Unknown task type: {task_type}",
                    'next_action': 'error'
                }
                
        except Exception as e:
            self.logger.error(f"Error executing plan: {e}")
            return {
                'success': False,
                'message': format_error_message(f"Error executing plan: {str(e)}"),
                'next_action': 'error'
            }

    def _handle_send_email(self, task_plan: Dict[str, Any], user_email: str = None) -> Dict[str, Any]:
        """Handle sending email tasks using Gemini for all content and subject, with personalized mails."""
        try:
            details = task_plan.get('details', {})
            recipients = details.get('recipients', [])
            # Handle special flag for missing recipients
            if recipients and recipients[0] == "__ASK_USER_FOR_EMPLOYEE__":
                return {
                    'success': False,
                    'message': "No recipient found. Please specify who to email.",
                    'next_action': 'clarify',
                    'missing_info': ['recipient']
                }
            # Build recipient_emails and recipient_names from team_contacts.json
            recipient_emails = []
            recipient_names = []
            from src.utils.validators import validate_email
            for r in recipients:
                if '@' in r and validate_email(r):
                    recipient_emails.append(r)
                    # Get name from team_contacts.json
                    name = self.name_matcher.team_contacts.get(r.lower(), {}).get('name')
                    if not name:
                        # Try to find by email in team_contacts
                        for member in self.name_matcher.get_team_members():
                            if member['email'].lower() == r.lower():
                                name = member['name']
                                break
                    recipient_names.append(name or r)
                else:
                    email = self.name_matcher.get_email_for_name(r)
                    if email:
                        recipient_emails.append(email)
                        # Get name from team_contacts.json
                        name = self.name_matcher.team_contacts.get(r.lower(), {}).get('name')
                        if not name:
                            for member in self.name_matcher.get_team_members():
                                if member['email'].lower() == email.lower():
                                    name = member['name']
                                    break
                        recipient_names.append(name or r)

            print(f"[Assistant] Final recipient_emails: {recipient_emails}, recipient_names: {recipient_names}")
            if not recipient_emails:
                return {
                    'success': False,
                    'message': "Could not find email addresses or names for the specified recipients.",
                    'next_action': 'clarify',
                    'missing_info': ['recipient']
                }
            # Always use sender name from user_profiles unless explicitly provided
            sender_name = details.get('sender_name')
            sender_email = user_email
            if not sender_name and sender_email:
                # Try to get name from email
                sender_name = self.user_manager.get_name_by_email(sender_email)
            elif sender_name and not sender_email:
                # Try to get email from name
                sender_email = self.user_manager.get_email_by_name(sender_name)
            if not sender_name:
                # fallback: use the first user in user_profiles.json
                users = self.user_manager.user_profiles.get("users", {})
                if users:
                    profile = list(users.values())[0]
                    sender_name = profile.get('name')
                    if not sender_email:
                        sender_email = profile.get('email')
            # Only use company name if explicitly provided in the query
            company_name = details.get('company_name') if 'company_name' in details else None
            missing_info = []
            if not sender_name:
                missing_info.append('your name')
            if missing_info:
                return {
                    'success': False,
                    'message': f"Please provide {', '.join(missing_info)} to personalize the email(s).",
                    'next_action': 'clarify',
                    'missing_info': missing_info
                }
            # Send personalized email to each recipient
            all_sent = True
            failed_recipients = []
            for rec_email, rec_name in zip(recipient_emails, recipient_names):
                # Prepare details for Gemini
                gemini_details = details.copy()
                gemini_details['recipient_name'] = rec_name
                gemini_details['recipient_email'] = rec_email
                gemini_details['sender_name'] = sender_name
                if company_name:
                    gemini_details['company_name'] = company_name
                # Check if user provided any keywords or bullet points in the message/details
                user_content = details.get('message', '').strip()
                # If no content, force Gemini to ask for info (only once)
                if not user_content or user_content.lower() in ['explain this project in detail', 'explaining this project in detail']:
                    return {
                        'success': False,
                        'message': 'Please provide some keywords, bullet points, or a brief description of the project so I can draft the email.',
                        'next_action': 'input_missing_fields',
                        'missing_fields': ['Project details (keywords, bullet points, or description)']
                    }
                if company_name:
                    gemini_prompt = (
                        f"Write a short, clear, personalized email to {rec_name} (email: {rec_email}) from {sender_name} at {company_name}. "
                        f"The purpose of the email is: {user_content}. "
                        f"If the user provides keywords or bullet points, expand them into a full, natural, friendly email. Do NOT use any placeholders or generic text like [Your Name], [Recipient Name], [Company], etc. Do NOT use a fixed template. Only use the data provided. If you have any content at all, generate the email. If you do not have any content, return a JSON with 'missing_fields' and do not generate the email. Return a JSON with 'subject' and 'body'."
                    )
                else:
                    gemini_prompt = (
                        f"Write a short, clear, personalized email to {rec_name} (email: {rec_email}) from {sender_name}. "
                        f"The purpose of the email is: {user_content}. "
                        f"If the user provides keywords or bullet points, expand them into a full, natural, friendly email. Do NOT use any placeholders or generic text like [Your Name], [Recipient Name], [Company], etc. Do NOT use a fixed template. Only use the data provided. If you have any content at all, generate the email. If you do not have any content, return a JSON with 'missing_fields' and do not generate the email. Return a JSON with 'subject' and 'body'."
                    )
                gemini_response = self.ai_service._generate_with_gemini(gemini_prompt)
                try:
                    import json
                    gemini_response_clean = gemini_response.strip()
                    if gemini_response_clean.startswith('```json'):
                        gemini_response_clean = gemini_response_clean[7:]
                    if gemini_response_clean.endswith('```'):
                        gemini_response_clean = gemini_response_clean[:-3]
                    gemini_json = json.loads(gemini_response_clean)
                    # If Gemini returns missing_fields, prompt user for input (only once)
                    if 'missing_fields' in gemini_json and gemini_json['missing_fields']:
                        if st.session_state.get('already_asked_for_missing', False):
                            # If already asked, just fail gracefully
                            return {
                                'success': False,
                                'message': 'Could not generate the email. Please provide more details.',
                                'next_action': 'error',
                                'missing_fields': gemini_json['missing_fields']
                            }
                        else:
                            st.session_state['already_asked_for_missing'] = True
                            return {
                                'success': False,
                                'message': f"Please provide the following missing information: {', '.join(gemini_json['missing_fields'])}",
                                'next_action': 'input_missing_fields',
                                'missing_fields': gemini_json['missing_fields']
                            }
                    subject = gemini_json.get('subject', 'No Subject')
                    content = gemini_json.get('body', gemini_response_clean)
                except Exception:
                    # Fallback: treat all as body
                    subject = f"Message for {rec_name}"
                    content = gemini_response
                sent = self.email_service.send_email(
                    to_emails=[rec_email],
                    subject=subject,
                    content=content,
                    from_email=sender_email or 'assistant@company.com'
                )
                if not sent:
                    all_sent = False
                    failed_recipients.append(rec_email)
            if all_sent:
                return {
                    'success': True,
                    'message': f"Personalized email(s) sent to {', '.join(recipient_emails)}.",
                    'next_action': 'complete'
                }
            else:
                return {
                    'success': False,
                    'message': f"Failed to send email(s) to: {', '.join(failed_recipients)}.",
                    'next_action': 'error',
                    'failed_recipients': failed_recipients
                }
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return {
                'success': False,
                'message': format_error_message(f"Error sending email: {str(e)}"),
                'next_action': 'error'
            }
    
    def _handle_meeting_scheduling(self, task_plan: Dict[str, Any], user_email: str = None) -> Dict[str, Any]:
        """Handle meeting scheduling tasks"""
        try:
            # Extract meeting details
            meeting_details = task_plan.get('details', {})
            # Always resolve employee emails from names
            employee_names = meeting_details.get('employees', [])
            employee_emails = self.name_matcher.get_emails_for_names(employee_names)
            target_date_str = meeting_details.get('date')

            if not target_date_str:
                return {
                    'success': False,
                    'message': "Please specify a date for the meeting.",
                    'next_action': 'clarify'
                }

            target_date = self._convert_date_string_to_date(target_date_str)

            if not target_date:
                return {
                    'success': False,
                    'message': "Could not parse the date. Please provide a valid date (e.g., '2023-10-27' or 'next Monday').",
                    'next_action': 'clarify'
                }

            # Check availability
            available_slots = self.calendar_service.find_available_slots(
                target_date,
                employee_emails + ([user_email] if user_email else []),
                meeting_details.get('duration', 60)
            )

            if not available_slots:
                return {
                    'success': False,
                    'message': "No available time slots found for the specified date and attendees.",
                    'next_action': 'suggest_alternatives'
                }

            # Present options to user (show all slots)
            options = []
            for i, slot in enumerate(available_slots, 1):
                options.append({
                    'id': i,
                    'time': f"{slot['start_time']} - {slot['end_time']}",
                    'duration': slot['duration']
                })

            return {
                'success': True,
                'message': f"I found {len(available_slots)} available time slots for your meeting.",
                'options': options,
                'meeting_details': meeting_details,
                'employee_emails': employee_emails,
                'next_action': 'select_time_slot'
            }

        except Exception as e:
            self.logger.error(f"Error handling meeting scheduling: {e}")
            return {
                'success': False,
                'message': format_error_message(f"Error scheduling meeting: {str(e)}"),
                'next_action': 'error'
            }
    
    def _handle_restaurant_booking(self, task_plan: Dict[str, Any], user_email: str = None) -> Dict[str, Any]:
        """Handle restaurant booking tasks"""
        try:
            # Extract restaurant details
            restaurant_details = task_plan.get('details', {})
            location = restaurant_details.get('location')
            cuisine = restaurant_details.get('cuisine')
            employees = restaurant_details.get('employees', [])
            # If location is missing or invalid, prompt user for area
            if not location or location.strip().lower() in ["about the team lunch.", "", None]:
                return {
                    'success': False,
                    'message': "Please specify an area or location for the restaurant search.",
                    'next_action': 'clarify',
                    'missing_info': ['location']
                }
            # Search for restaurants using Google Places and OpenTripMap APIs only
            restaurants = self.restaurant_service.search_restaurants(
                location=location,
                cuisine=cuisine,
                min_rating=3.5
            )
            if not restaurants:
                return {
                    'success': False,
                    'message': f"No restaurants found in {location} matching your criteria. Try a different location or cuisine.",
                    'next_action': 'suggest_alternatives'
                }
            # Prepare options for user (top 5)
            options = []
            for i, restaurant in enumerate(restaurants[:5], 1):
                options.append({
                    'id': i,
                    'name': restaurant.get('name'),
                    'address': restaurant.get('address'),
                    'cuisine': restaurant.get('cuisine', 'Various'),
                    'rating': restaurant.get('rating', 0),
                    'price_level': restaurant.get('price_level', 'N/A'),
                    'phone': restaurant.get('phone', 'N/A'),
                    'website': restaurant.get('website', ''),
                    'hours': restaurant.get('opening_hours', []),
                    'source': restaurant.get('source', 'Unknown'),
                    'user_ratings_total': restaurant.get('user_ratings_total', 0),
                    'business_status': restaurant.get('business_status', ''),
                    'reviews': restaurant.get('reviews', [])
                })
            # If employees is the special flag, prompt for employees
            if employees and employees[0] == "__ASK_USER_FOR_EMPLOYEE__":
                return {
                    'success': False,
                    'message': "No employees specified for the dinner. Please specify who to invite.",
                    'next_action': 'clarify',
                    'missing_info': ['employees']
                }
            # If 'everyone' or similar, get all team emails
            if employees and set(employees) == set([member['name'] for member in self.name_matcher.get_team_members()]):
                attendee_emails = [member['email'] for member in self.name_matcher.get_team_members()]
            else:
                attendee_emails = self.name_matcher.get_emails_for_names(employees)
            # After user selects a restaurant, send dinner invite
            # (In a real system, this would be a follow-up action after user selection)
            # For now, just return options and wait for user selection
            return {
                'success': True,
                'message': f"I found {len(restaurants)} restaurants in {location} matching your criteria. Here are the top options:",
                'options': options,
                'restaurant_details': restaurant_details,
                'attendee_emails': attendee_emails,
                'all_restaurants': options,
                'next_action': 'select_restaurant'
            }
        except Exception as e:
            self.logger.error(f"Error handling restaurant booking: {e}")
            return {
                'success': False,
                'message': format_error_message(f"Error searching restaurants: {str(e)}"),
                'next_action': 'error'
            }
    
    def _handle_availability_check(self, task_plan: Dict[str, Any], user_email: str = None) -> Dict[str, Any]:
        """Handle availability checking tasks"""
        try:
            # Extract availability details
            availability_details = task_plan.get('details', {})
            employee_emails = task_plan.get('employee_emails', [])
            target_date_str = availability_details.get('date')
            
            if not target_date_str:
                return {
                    'success': False,
                    'message': "Please specify a date to check availability.",
                    'next_action': 'clarify'
                }
            
            target_date = self._convert_date_string_to_date(target_date_str)
            
            if not target_date:
                return {
                    'success': False,
                    'message': "Could not parse the date. Please provide a valid date (e.g., '2023-10-27' or 'next Monday').",
                    'next_action': 'clarify'
                }
            
            # Get user schedules
            schedules = {}
            for email in employee_emails:
                schedule = self.calendar_service.get_user_schedule(
                    email, target_date, target_date
                )
                schedules[email] = schedule
            
            return {
                'success': True,
                'message': f"Availability checked for {len(employee_emails)} team members.",
                'schedules': schedules,
                'target_date': target_date,
                'next_action': 'display_schedules'
            }
            
        except Exception as e:
            self.logger.error(f"Error handling availability check: {e}")
            return {
                'success': False,
                'message': format_error_message(f"Error checking availability: {str(e)}"),
                'next_action': 'error'
            }
    
    def confirm_action(self, action_type: str, action_details: Dict[str, Any], 
                      user_email: str = None) -> Dict[str, Any]:
        """
        Confirm and execute a user-selected action
        
        Args:
            action_type: Type of action to confirm
            action_details: Details of the action
            user_email: User's email address
        
        Returns:
            Dictionary with confirmation results
        """
        try:
            if action_type == 'meeting_scheduling':
                return self._confirm_meeting_scheduling(action_details, user_email)
            elif action_type == 'restaurant_booking':
                return self._confirm_restaurant_booking(action_details, user_email)
            else:
                return {
                    'success': False,
                    'message': f"Unknown action type: {action_type}",
                    'next_action': 'error'
                }
                
        except Exception as e:
            self.logger.error(f"Error confirming action: {e}")
            return {
                'success': False,
                'message': format_error_message(f"Error confirming action: {str(e)}"),
                'next_action': 'error'
            }
    
    def _confirm_meeting_scheduling(self, action_details: Dict[str, Any], user_email: str = None) -> Dict[str, Any]:
        """Confirm and create the meeting event, send notification, and return result."""
        try:
            # Get organizer profile
            organizer_profile = self.user_manager.get_user_profile(user_email) or {
                'name': user_email,
                'email': user_email
            }
            # Use selected time from UI if present
            selected_time = action_details.get('selected_time') or action_details.get('time')
            if not selected_time:
                return {
                    'success': False,
                    'message': 'No time slot selected. Please select a time slot for the meeting.',
                    'next_action': 'clarify'
                }
            # Prepare event details
            event_details = {
                'title': action_details.get('title', 'Team Meeting'),
                'date': action_details.get('date'),
                'time': selected_time,
                'duration': action_details.get('duration', 60),
                'location': action_details.get('location', 'N/A'),
                'attendees': action_details.get('attendees', []),
                'organizer': organizer_profile.get('email'),
                'timezone': action_details.get('timezone', 'UTC'),
            }
            # Final conflict check before event creation
            from datetime import datetime, timedelta
            from src.services.calendar_service import CalendarService
            calendar_service = CalendarService()
            start_time = selected_time
            try:
                end_time = (datetime.strptime(start_time, '%H:%M') + timedelta(minutes=event_details['duration'])).strftime('%H:%M')
            except Exception:
                end_time = start_time  # fallback, should not happen
            conflict_check = calendar_service.check_availability(
                event_details['date'],
                start_time,
                end_time,
                event_details['attendees']
            )
            if not conflict_check['available']:
                return {
                    'success': False,
                    'message': 'The selected time slot is no longer available for all attendees. Please choose another slot.',
                    'conflicts': conflict_check['conflicts'],
                    'next_action': 'select_time_slot'
                }
            # Create the calendar event
            event_created = self.calendar_service.create_event(event_details)
            # Send meeting invite email to all attendees
            email_sent = self.email_service.send_meeting_invite(event_details, event_details['attendees'], organizer_profile)
            if event_created and email_sent:
                return {
                    'success': True,
                    'message': 'Meeting scheduled, calendar event created, and notification email sent to all attendees.',
                    'next_action': 'complete'
                }
            elif event_created:
                return {
                    'success': True,
                    'message': 'Meeting scheduled and calendar event created, but failed to send notification email.',
                    'next_action': 'complete'
                }
            elif email_sent:
                return {
                    'success': True,
                    'message': 'Meeting notification email sent, but failed to create calendar event.',
                    'next_action': 'complete'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to schedule meeting: could not create calendar event or send notification email.',
                    'next_action': 'error'
                }
        except Exception as e:
            self.logger.error(f"Error confirming meeting scheduling: {e}")
            return {
                'success': False,
                'message': format_error_message(f"Error confirming meeting: {str(e)}"),
                'next_action': 'error'
            }

    def _confirm_restaurant_booking(self, action_details: Dict[str, Any], user_email: str = None) -> Dict[str, Any]:
        """Confirm and execute restaurant booking"""
        try:
            # For demo purposes, we'll simulate a booking
            # In a real implementation, you'd integrate with restaurant booking APIs
            
            restaurant_name = action_details.get('name', 'Restaurant')
            booking_date_str = action_details.get('date', 'TBD')
            booking_time_str = action_details.get('time', 'TBD')
            
            booking_date = self._convert_date_string_to_date(booking_date_str)
            booking_time = self._convert_date_string_to_date(booking_time_str)
            
            if not booking_date:
                return {
                    'success': False,
                    'message': "Could not parse the booking date. Please provide a valid date (e.g., '2023-10-27' or 'next Monday').",
                    'next_action': 'clarify'
                }
            
            if not booking_time:
                return {
                    'success': False,
                    'message': "Could not parse the booking time. Please provide a valid time (e.g., '18:00' or '6 PM').",
                    'next_action': 'clarify'
                }
            
            # Always send dinner invites after booking
            attendee_emails = action_details.get('attendees', [])
            invites_sent = False
            if attendee_emails:
                invites_sent = self.email_service.send_dinner_invite(
                    action_details, attendee_emails, user_email or 'assistant@company.com'
                )
            if invites_sent:
                return {
                    'success': True,
                    'message': format_success_message(
                        f"Dinner booking confirmed at {restaurant_name}! Invites sent to {len(attendee_emails)} attendees."
                    ),
                    'next_action': 'complete'
                }
            else:
                return {
                    'success': True,
                    'message': format_success_message(
                        f"Dinner booking confirmed at {restaurant_name}! However, there was an issue sending invites."
                    ),
                    'next_action': 'complete'
                }
        except Exception as e:
            self.logger.error(f"Error confirming restaurant booking: {e}")
            return {
                'success': False,
                'message': format_error_message(f"Error booking restaurant: {str(e)}"),
                'next_action': 'error'
            }
    
    def delete_event_and_notify(self, event_id: str, event_details: Dict[str, Any], user_email: str = None) -> Dict[str, Any]:
        """Delete an event and notify attendees"""
        try:
            deleted = self.calendar_service.delete_event(event_id)
            if not deleted:
                return {
                    'success': False,
                    'message': f"Failed to delete event with ID {event_id}.",
                    'next_action': 'error'
                }
            # Send cancellation email to attendees
            attendee_emails = event_details.get('attendees', [])
            if attendee_emails:
                subject = f"Meeting/Event Cancelled: {event_details.get('title', 'Event')} on {event_details.get('date', 'TBD')}"
                content = f"""
Dear Team,

The following event has been cancelled:
- Title: {event_details.get('title', 'Event')}
- Date: {event_details.get('date', 'TBD')}
- Time: {event_details.get('time', 'TBD')}
- Location: {event_details.get('location', 'TBD')}

We apologize for any inconvenience.

Best regards,
{user_email}
"""
                self.email_service.send_email(
                    to_emails=attendee_emails,
                    subject=subject,
                    content=content,
                    from_email=user_email or 'assistant@company.com'
                )
            return {
                'success': True,
                'message': f"Event deleted and attendees notified.",
                'next_action': 'complete'
            }
        except Exception as e:
            self.logger.error(f"Error deleting event: {e}")
            return {
                'success': False,
                'message': f"Error deleting event: {str(e)}",
                'next_action': 'error'
            }
    
    def cancel_events_for_users_on_date(self, user_emails: list, target_date: str, acting_user_email: str = None) -> Dict[str, Any]:
        """Cancel all events for the given users on the specified date, and notify attendees."""
        try:
            deleted_count = 0
            failed = []
            for email in user_emails:
                # Get all events for this user on the date
                events = self.calendar_service.get_events(target_date, target_date, user_email=email)
                for event in events:
                    event_id = event.get('id')
                    if not event_id:
                        failed.append({'user': email, 'event': event, 'reason': 'No event ID'})
                        continue
                    result = self.delete_event_and_notify(event_id, event, acting_user_email or email)
                    if result.get('success'):
                        deleted_count += 1
                    else:
                        failed.append({'user': email, 'event': event, 'reason': result.get('message')})
            return {
                'success': True,
                'message': f"Deleted {deleted_count} events. {len(failed)} failed.",
                'deleted_count': deleted_count,
                'failed': failed
            }
        except Exception as e:
            self.logger.error(f"Error cancelling events: {e}")
            return {
                'success': False,
                'message': f"Error cancelling events: {str(e)}",
                'next_action': 'error'
            }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.logger.info("Conversation history cleared")
    
    def get_assistant_status(self) -> Dict[str, Any]:
        """Get assistant status and capabilities"""
        return {
            'status': 'active',
            'capabilities': [
                'meeting_scheduling',
                'restaurant_booking',
                'availability_checking',
                'email_sending',
                'calendar_management'
            ],
            'services': {
                'ai_service': 'gemini',  # AIService uses Gemini API
                'calendar_service': self.calendar_service.service,
                'email_service': self.email_service.service,
                'location_service': self.location_service.service,
                'restaurant_service': self.restaurant_service.service
            },
            'conversation_count': len(self.conversation_history)
        } 