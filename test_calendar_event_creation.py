#!/usr/bin/env python3
"""
Test script to diagnose Google Calendar API issues and test event creation
"""
import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from src.services.calendar_service import CalendarService
from config.settings import CALENDAR_SERVICE

def test_calendar_service_initialization():
    """Test if calendar service can be initialized properly"""
    print("=" * 60)
    print("TEST 1: Calendar Service Initialization")
    print("=" * 60)
    
    try:
        print(f"Calendar Service Type: {CALENDAR_SERVICE}")
        
        # Check for credential files in config directory
        config_dir = Path("config")
        credential_files = list(config_dir.glob("*.json"))
        
        print(f"Found credential files in config directory:")
        for file in credential_files:
            print(f"  - {file.name}")
            if file.name in ["credentials.json", "gmail_credentials.json"]:
                try:
                    with open(file, 'r') as f:
                        content = json.load(f)
                        print(f"    Type: {content.get('type', 'unknown')}")
                        print(f"    Project ID: {content.get('project_id', 'unknown')}")
                except Exception as e:
                    print(f"    Error reading file: {e}")
        
        # Check for token files
        token_files = [f for f in credential_files if "token" in f.name.lower()]
        print(f"\nToken files found:")
        for file in token_files:
            print(f"  - {file.name}")
            try:
                with open(file, 'r') as f:
                    content = json.load(f)
                    print(f"    Has refresh_token: {'refresh_token' in content}")
                    print(f"    Has access_token: {'access_token' in content}")
                    print(f"    Token type: {content.get('token_type', 'unknown')}")
            except Exception as e:
                print(f"    Error reading file: {e}")
        
        # Try to initialize calendar service
        calendar_service = CalendarService()
        print(f"\n✅ Calendar service initialized successfully!")
        print(f"Service type: {calendar_service.service}")
        print(f"Google service available: {calendar_service.google_service is not None}")
        
        return calendar_service
        
    except Exception as e:
        print(f"❌ Failed to initialize calendar service: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return None

def test_google_calendar_api_connection(calendar_service):
    """Test Google Calendar API connection"""
    print("\n" + "=" * 60)
    print("TEST 2: Google Calendar API Connection")
    print("=" * 60)
    
    if not calendar_service or not calendar_service.google_service:
        print("❌ Google Calendar service not available")
        return False
    
    try:
        # Test API connection by listing calendars
        calendar_list = calendar_service.google_service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        print(f"✅ Successfully connected to Google Calendar API!")
        print(f"Found {len(calendars)} calendars:")
        
        for calendar in calendars[:3]:  # Show first 3 calendars
            print(f"  - {calendar.get('summary', 'Unknown')} ({calendar.get('id', 'No ID')})")
        
        if len(calendars) > 3:
            print(f"  ... and {len(calendars) - 3} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Google Calendar API: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_event_creation(calendar_service):
    """Test creating a simple event"""
    print("\n" + "=" * 60)
    print("TEST 3: Event Creation")
    print("=" * 60)
    
    if not calendar_service:
        print("❌ Calendar service not available")
        return False
    
    try:
        # Create test event details
        tomorrow = datetime.now() + timedelta(days=1)
        test_event = {
            'title': 'Test Meeting - Calendar API Test',
            'date': tomorrow.strftime('%Y-%m-%d'),
            'time': '14:00',
            'duration': 30,
            'description': 'This is a test event created by the calendar API test script',
            'location': 'Test Location',
            'attendees': ['test@example.com'],
            'timezone': 'UTC'
        }
        
        print(f"Creating test event:")
        print(f"  Title: {test_event['title']}")
        print(f"  Date: {test_event['date']}")
        print(f"  Time: {test_event['time']}")
        print(f"  Duration: {test_event['duration']} minutes")
        print(f"  Attendees: {test_event['attendees']}")
        
        # Try to create the event
        success = calendar_service.create_event(test_event)
        
        if success:
            print("✅ Event created successfully!")
            return True
        else:
            print("❌ Event creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error creating event: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_event_retrieval(calendar_service):
    """Test retrieving events"""
    print("\n" + "=" * 60)
    print("TEST 4: Event Retrieval")
    print("=" * 60)
    
    if not calendar_service:
        print("❌ Calendar service not available")
        return False
    
    try:
        # Get events for today
        today = datetime.now().date()
        events = calendar_service.get_events(today, today)
        
        print(f"✅ Successfully retrieved events for {today}")
        print(f"Found {len(events)} events today:")
        
        for event in events[:5]:  # Show first 5 events
            print(f"  - {event.get('title', 'No title')} at {event.get('start_time', 'No time')}")
        
        if len(events) > 5:
            print(f"  ... and {len(events) - 5} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Error retrieving events: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_availability_checking(calendar_service):
    """Test availability checking"""
    print("\n" + "=" * 60)
    print("TEST 5: Availability Checking")
    print("=" * 60)
    
    if not calendar_service:
        print("❌ Calendar service not available")
        return False
    
    try:
        # Check availability for tomorrow
        tomorrow = datetime.now() + timedelta(days=1)
        available_slots = calendar_service.find_available_slots(
            tomorrow.date(), 
            ['test@example.com'], 
            60
        )
        
        print(f"✅ Successfully checked availability for {tomorrow.date()}")
        print(f"Found {len(available_slots)} available slots:")
        
        for slot in available_slots[:3]:  # Show first 3 slots
            print(f"  - {slot.get('start_time', 'No start')} to {slot.get('end_time', 'No end')}")
        
        if len(available_slots) > 3:
            print(f"  ... and {len(available_slots) - 3} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking availability: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_assistant_integration():
    """Test the assistant's meeting confirmation flow"""
    print("\n" + "=" * 60)
    print("TEST 6: Assistant Integration Test")
    print("=" * 60)
    
    try:
        from src.core.assistant import Assistant
        
        assistant = Assistant()
        
        # Create test meeting details similar to what the app would pass
        tomorrow = datetime.now() + timedelta(days=1)
        meeting_details = {
            'title': 'Test Meeting from Assistant',
            'date': tomorrow.strftime('%Y-%m-%d'),
            'time': '15:00',
            'duration': 45,
            'description': 'Test meeting created by assistant integration test',
            'location': 'Conference Room A',
            'attendees': ['test@example.com'],
            'timezone': 'UTC'
        }
        
        print(f"Testing assistant confirm_action with meeting details:")
        print(f"  Title: {meeting_details['title']}")
        print(f"  Date: {meeting_details['date']}")
        print(f"  Time: {meeting_details['time']}")
        print(f"  Attendees: {meeting_details['attendees']}")
        
        # Test the confirm_action method
        result = assistant.confirm_action('meeting_scheduling', meeting_details, 'test@company.com')
        
        print(f"Assistant confirm_action result:")
        print(f"  Success: {result.get('success', False)}")
        print(f"  Message: {result.get('message', 'No message')}")
        print(f"  Next Action: {result.get('next_action', 'None')}")
        
        if result.get('success'):
            print("✅ Assistant integration test passed!")
            return True
        else:
            print("❌ Assistant integration test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in assistant integration test: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Google Calendar API Diagnostic Test")
    print("=" * 60)
    
    # Test 1: Service initialization
    calendar_service = test_calendar_service_initialization()
    
    # Test 2: API connection
    api_connected = test_google_calendar_api_connection(calendar_service)
    
    # Test 3: Event creation
    event_created = False
    if api_connected:
        event_created = test_event_creation(calendar_service)
    
    # Test 4: Event retrieval
    events_retrieved = False
    if api_connected:
        events_retrieved = test_event_retrieval(calendar_service)
    
    # Test 5: Availability checking
    availability_checked = False
    if api_connected:
        availability_checked = test_availability_checking(calendar_service)
    
    # Test 6: Assistant integration
    assistant_works = test_assistant_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Service Initialization: {'PASS' if calendar_service else 'FAIL'}")
    print(f"✅ API Connection: {'PASS' if api_connected else 'FAIL'}")
    print(f"✅ Event Creation: {'PASS' if event_created else 'FAIL'}")
    print(f"✅ Event Retrieval: {'PASS' if events_retrieved else 'FAIL'}")
    print(f"✅ Availability Checking: {'PASS' if availability_checked else 'FAIL'}")
    print(f"✅ Assistant Integration: {'PASS' if assistant_works else 'FAIL'}")
    
    # Recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    if not calendar_service:
        print("❌ Fix calendar service initialization first")
        print("   - Check Google Calendar credentials file")
        print("   - Verify token file exists and is valid")
        print("   - Ensure all required dependencies are installed")
    
    elif not api_connected:
        print("❌ Fix Google Calendar API connection")
        print("   - Verify API credentials are correct")
        print("   - Check if token needs refresh")
        print("   - Ensure calendar API is enabled in Google Cloud Console")
    
    elif not event_created:
        print("❌ Fix event creation")
        print("   - Check calendar permissions")
        print("   - Verify event data format")
        print("   - Check for API quotas or rate limits")
    
    elif not assistant_works:
        print("❌ Fix assistant integration")
        print("   - Check action_details format passed to confirm_action")
        print("   - Verify calendar_service.create_event call")
        print("   - Check error handling in _confirm_meeting_scheduling")
    
    else:
        print("✅ All tests passed! Calendar functionality should work correctly.")

if __name__ == "__main__":
    main() 