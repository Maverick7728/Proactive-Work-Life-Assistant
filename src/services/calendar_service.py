"""
Calendar Service for managing events and availability (supports Google Calendar and local SQLite)
"""
import os
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from config.settings import CALENDAR_SERVICE, CALENDAR_DB_PATH, DEFAULT_MEETING_DURATION, BUFFER_TIME
from src.services.email_service import EmailService

# Google Calendar imports
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarService:
    """
    Calendar service for managing events and checking availability
    Uses Google Calendar API only (no local fallback)
    Supports multi-user cal_token.json
    """
    
    def __init__(self, user_email=None):
        self.service = "google"
        self.db_path = Path(CALENDAR_DB_PATH)  # Not used, but kept for compatibility
        self.google_creds = None
        self.google_service = None
        self.email_service = EmailService()
        self.active_user_email = user_email
        self._init_google_calendar(user_email)

    def _init_google_calendar(self, user_email=None):
        token_path = os.getenv("GOOGLE_CALENDAR_TOKEN", "config/cal_token.json")
        if not os.path.exists(token_path):
            raise EnvironmentError(f"GOOGLE_CALENDAR_TOKEN file not found at {token_path}.")
        with open(token_path, "r", encoding="utf-8") as f:
            all_tokens = json.load(f)
        if not user_email:
            user_email = list(all_tokens.keys())[0]
        if user_email not in all_tokens:
            raise ValueError(f"No token found for user {user_email} in {token_path}")
        user_token = all_tokens[user_email]
        creds = Credentials.from_authorized_user_info(user_token, SCOPES)
        self.google_creds = creds
        self.google_service = build('calendar', 'v3', credentials=creds)
        self.active_user_email = user_email

    def switch_user(self, user_email):
        self._init_google_calendar(user_email)

    def create_event(self, event_details: Dict[str, Any]) -> bool:
        result = self._create_event_google(event_details)
        if result:
            self.email_service.send_event_notification(event_details, 'created', event_details.get('organizer', 'assistant@company.com'))
        return result

    def _create_event_google(self, event_details: Dict[str, Any]) -> bool:
        try:
            start_time = self._parse_datetime(event_details['date'], event_details['time'])
            duration = event_details.get('duration', DEFAULT_MEETING_DURATION)
            end_time = start_time + timedelta(minutes=duration)
            timezone = event_details.get('timezone', 'Asia/Kolkata')
            event = {
                'summary': event_details.get('title', 'Meeting'),
                'location': event_details.get('location', ''),
                'description': event_details.get('description', ''),
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': timezone,
                },
                'attendees': [{'email': email} for email in event_details.get('attendees', [])],
            }
            self.google_service.events().insert(calendarId='primary', body=event).execute()
            return True
        except Exception as e:
            print(f"Google Calendar API error: {e}")
            return False

    def get_events(self, start_date, end_date, user_email: str = None) -> List[Dict[str, Any]]:
        start_date_obj = self._ensure_date_object(start_date)
        end_date_obj = self._ensure_date_object(end_date)
        if not start_date_obj or not end_date_obj:
            print(f"Error getting events: Invalid date format - start_date: {start_date}, end_date: {end_date}")
            return []
        return self._get_events_google(start_date_obj, end_date_obj, user_email)

    def _get_events_google(self, start_date: date, end_date: date, user_email: str = None) -> List[Dict[str, Any]]:
        try:
            events = []
            time_min = datetime.combine(start_date, datetime.min.time()).isoformat() + 'Z'
            time_max = datetime.combine(end_date, datetime.max.time()).isoformat() + 'Z'
            calendar_id = 'primary'
            results = self.google_service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            for event in results.get('items', []):
                events.append({
                    'id': event.get('id'),
                    'title': event.get('summary', ''),
                    'description': event.get('description', ''),
                    'start_time': event['start'].get('dateTime', event['start'].get('date')),
                    'end_time': event['end'].get('dateTime', event['end'].get('date')),
                    'location': event.get('location', ''),
                    'attendees': [att['email'] for att in event.get('attendees', [])] if event.get('attendees') else [],
                    'organizer': event.get('organizer', {}).get('email', '')
                })
            return events
        except Exception as e:
            print(f"Error getting events from Google Calendar: {e}")
            return []

    def delete_event(self, event_id: str) -> bool:
        event_details = self._get_event_details_by_id(event_id)
        result = self._delete_event_google(event_id)
        if result and event_details:
            self.email_service.send_event_notification(event_details, 'deleted', event_details.get('organizer', 'assistant@company.com'))
        return result

    def _delete_event_google(self, event_id: str) -> bool:
        try:
            self.google_service.events().delete(calendarId='primary', eventId=event_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting event from Google Calendar: {e}")
            return False

    def update_event(self, event_id: str, event_details: Dict[str, Any]) -> bool:
        result = self._update_event_google(event_id, event_details)
        if result:
            self.email_service.send_event_notification(event_details, 'modified', event_details.get('organizer', 'assistant@company.com'))
        return result

    def _update_event_google(self, event_id: str, event_details: Dict[str, Any]) -> bool:
        try:
            # Google Calendar API does not have a direct "update event by ID"; you must patch the event
            self.google_service.events().patch(calendarId='primary', eventId=event_id, body=event_details).execute()
            return True
        except Exception as e:
            print(f"Error updating event in Google Calendar: {e}")
            return False

    def find_available_slots(self, target_date, user_emails: List[str], duration_minutes: int = 60) -> List[Dict[str, Any]]:
        target_date_obj = self._ensure_date_object(target_date)
        if not target_date_obj:
            print(f"Error finding available slots: Invalid date format - target_date: {target_date}")
            return []
        return self._find_available_slots_google(target_date_obj, user_emails, duration_minutes)

    def _find_available_slots_google(self, target_date: date, user_emails: List[str], duration_minutes: int = 60) -> List[Dict[str, Any]]:
        try:
            working_hours = self._get_working_hours()
            events = self.get_events(target_date, target_date)
            slots = []
            current_time = working_hours['start']
            while current_time < working_hours['end']:
                slot_end = current_time + timedelta(minutes=duration_minutes)
                if slot_end <= working_hours['end']:
                    availability = self.check_availability(
                        target_date,
                        current_time.strftime('%H:%M'),
                        slot_end.strftime('%H:%M'),
                        user_emails
                    )
                    if availability['available']:
                        slots.append({
                            'start_time': current_time.strftime('%H:%M'),
                            'end_time': slot_end.strftime('%H:%M'),
                            'time': f"{current_time.strftime('%H:%M')} - {slot_end.strftime('%H:%M')}",
                            'duration': duration_minutes
                        })
                current_time += timedelta(minutes=30)
            return slots
        except Exception as e:
            print(f"Error finding available slots from Google Calendar: {e}")
            return []

    def check_availability(self, target_date, start_time: str, end_time: str, user_emails: List[str]) -> Dict[str, Any]:
        target_date_obj = self._ensure_date_object(target_date)
        if not target_date_obj:
            print(f"Error checking availability: Invalid date format - target_date: {target_date}")
            return {
                'available': False,
                'available_users': [],
                'conflicts': [],
                'error': f"Invalid date format: {target_date}"
            }
        return self._check_availability_google(target_date_obj, start_time, end_time, user_emails)

    def _check_availability_google(self, target_date: date, start_time: str, end_time: str, user_emails: List[str]) -> Dict[str, Any]:
        try:
            requested_start = self._parse_datetime(target_date, start_time)
            requested_end = self._parse_datetime(target_date, end_time)
            available_users = []
            conflicts = []
            for email in user_emails:
                try:
                    events = []
                    time_min = requested_start.isoformat() + 'Z'
                    time_max = requested_end.isoformat() + 'Z'
                    results = self.google_service.events().list(
                        calendarId=email,
                        timeMin=time_min,
                        timeMax=time_max,
                        singleEvents=True,
                        orderBy='startTime'
                    ).execute()
                    for event in results.get('items', []):
                        event_start = event['start'].get('dateTime', event['start'].get('date'))
                        event_end = event['end'].get('dateTime', event['end'].get('date'))
                        event_start_dt = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
                        event_end_dt = datetime.fromisoformat(event_end.replace('Z', '+00:00'))
                        if (requested_start < event_end_dt and requested_end > event_start_dt):
                            conflicts.append({'user': email, 'event': event})
                            break
                    else:
                        available_users.append(email)
                except Exception as e:
                    conflicts.append({'user': email, 'error': str(e)})
            return {
                'available': len(available_users) == len(user_emails),
                'available_users': available_users,
                'conflicts': conflicts,
                'requested_slot': {
                    'start': requested_start.isoformat(),
                    'end': requested_end.isoformat()
                }
            }
        except Exception as e:
            print(f"Error checking availability from Google Calendar: {e}")
            return {
                'available': False,
                'available_users': [],
                'conflicts': [],
                'error': str(e)
            }

    def _get_working_hours(self) -> Dict[str, datetime]:
        # Example: 9am to 6pm
        today = datetime.now()
        return {
            'start': today.replace(hour=9, minute=0, second=0, microsecond=0),
            'end': today.replace(hour=18, minute=0, second=0, microsecond=0)
        }

    def _parse_datetime(self, date_input, time_str: str) -> datetime:
        if isinstance(date_input, str):
            date_obj = datetime.strptime(date_input, "%Y-%m-%d")
        else:
            date_obj = date_input
        try:
            time_obj = datetime.strptime(time_str, "%H:%M")
        except Exception:
            for fmt in ["%H:%M", "%I:%M%p", "%I%p"]:
                try:
                    time_obj = datetime.strptime(time_str, fmt)
                    break
                except ValueError:
                    continue
            if not time_obj:
                raise ValueError(f"Could not parse time: {time_str}")
        return datetime.combine(date_obj, time_obj.time())

    def _ensure_date_object(self, date_input) -> Optional[date]:
        if isinstance(date_input, date):
            return date_input
        elif isinstance(date_input, datetime):
            return date_input.date()
        elif isinstance(date_input, str):
            try:
                from dateutil.parser import parse as dateutil_parse
                return dateutil_parse(date_input, fuzzy=True).date()
            except Exception:
                try:
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']:
                        try:
                            return datetime.strptime(date_input, fmt).date()
                        except ValueError:
                            continue
                except Exception:
                    print(f"Error parsing datetime: Could not parse date: {date_input}")
                    return None
        return None

    def _get_event_details_by_id(self, event_id: str) -> dict:
        # Not implemented for Google Calendar, return minimal info
        return {'id': event_id, 'title': '', 'date': '', 'time': '', 'location': '', 'attendees': [], 'organizer': ''} 