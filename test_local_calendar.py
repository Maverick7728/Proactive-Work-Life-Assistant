#!/usr/bin/env python3
"""
Test script to verify local SQLite calendar service is working
"""
import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from src.services.calendar_service import CalendarService
from config.settings import CALENDAR_SERVICE, CALENDAR_DB_PATH

def test_local_calendar_service():
    """Test the local SQLite calendar service"""
    print("=" * 60)
    print("LOCAL CALENDAR SERVICE TEST")
    print("=" * 60)
    
    print(f"Calendar Service Type: {CALENDAR_SERVICE}")
    print(f"Database Path: {CALENDAR_DB_PATH}")
    
    try:
        # Initialize calendar service
        calendar_service = CalendarService()
        print(f"✅ Calendar service initialized successfully!")
        print(f"Service type: {calendar_service.service}")
        print(f"Database path: {calendar_service.db_path}")
        
        # Test event creation
        tomorrow = datetime.now() + timedelta(days=1)
        test_event = {
            'title': 'Test Meeting - Local Calendar Test',
            'date': tomorrow.strftime('%Y-%m-%d'),
            'time': '14:00',
            'duration': 30,
            'description': 'This is a test event created by the local calendar test script',
            'location': 'Test Location',
            'attendees': ['test@example.com'],
            'timezone': 'UTC'
        }
        
        print(f"\nCreating test event:")
        print(f"  Title: {test_event['title']}")
        print(f"  Date: {test_event['date']}")
        print(f"  Time: {test_event['time']}")
        print(f"  Duration: {test_event['duration']} minutes")
        print(f"  Attendees: {test_event['attendees']}")
        
        # Create the event
        success = calendar_service.create_event(test_event)
        
        if success:
            print("✅ Event created successfully in local database!")
        else:
            print("❌ Event creation failed")
            return False
        
        # Test event retrieval
        print(f"\nRetrieving events for {tomorrow.date()}:")
        events = calendar_service.get_events(tomorrow.date(), tomorrow.date())
        
        print(f"Found {len(events)} events:")
        for event in events:
            print(f"  - {event.get('title', 'No title')} at {event.get('start_time', 'No time')}")
            print(f"    Description: {event.get('description', 'No description')}")
            print(f"    Location: {event.get('location', 'No location')}")
            print(f"    Attendees: {event.get('attendees', 'No attendees')}")
        
        # Test availability checking
        print(f"\nChecking availability for {tomorrow.date()}:")
        available_slots = calendar_service.find_available_slots(
            tomorrow.date(), 
            ['test@example.com'], 
            60
        )
        
        print(f"Found {len(available_slots)} available slots:")
        for slot in available_slots[:3]:
            print(f"  - {slot.get('start_time', 'No start')} to {slot.get('end_time', 'No end')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in local calendar test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_assistant_with_local_calendar():
    """Test the assistant with local calendar service"""
    print("\n" + "=" * 60)
    print("ASSISTANT WITH LOCAL CALENDAR TEST")
    print("=" * 60)
    
    try:
        from src.core.assistant import Assistant
        
        assistant = Assistant()
        
        # Create test meeting details
        tomorrow = datetime.now() + timedelta(days=1)
        meeting_details = {
            'title': 'Test Meeting from Assistant - Local',
            'date': tomorrow.strftime('%Y-%m-%d'),
            'time': '15:00',
            'duration': 45,
            'description': 'Test meeting created by assistant with local calendar',
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
        
        print(f"\nAssistant confirm_action result:")
        print(f"  Success: {result.get('success', False)}")
        print(f"  Message: {result.get('message', 'No message')}")
        print(f"  Next Action: {result.get('next_action', 'None')}")
        
        if result.get('success'):
            print("✅ Assistant with local calendar test passed!")
            
            # Verify the event was actually created
            calendar_service = assistant.calendar_service
            events = calendar_service.get_events(tomorrow.date(), tomorrow.date())
            
            print(f"\nVerifying event was created in database:")
            print(f"Found {len(events)} events in database:")
            for event in events:
                print(f"  - {event.get('title', 'No title')} at {event.get('start_time', 'No time')}")
            
            return True
        else:
            print("❌ Assistant with local calendar test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in assistant test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Local Calendar Service Diagnostic Test")
    print("=" * 60)
    
    # Test 1: Local calendar service
    local_works = test_local_calendar_service()
    
    # Test 2: Assistant with local calendar
    assistant_works = test_assistant_with_local_calendar()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Local Calendar Service: {'PASS' if local_works else 'FAIL'}")
    print(f"✅ Assistant Integration: {'PASS' if assistant_works else 'FAIL'}")
    
    # Recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    if local_works and assistant_works:
        print("✅ Local calendar service is working correctly!")
        print("   - Events are being created in the SQLite database")
        print("   - Assistant is successfully creating events")
        print("   - The issue is that you want Google Calendar integration")
        print("\nTo enable Google Calendar integration:")
        print("1. Set CALENDAR_SERVICE=google in your environment")
        print("2. Ensure you have proper Google Calendar credentials")
        print("3. Place credentials.json in the config directory")
        print("4. Run the OAuth flow to get a valid token")
    
    elif not local_works:
        print("❌ Local calendar service is not working")
        print("   - Check database permissions")
        print("   - Verify SQLite is working")
        print("   - Check for any database errors")
    
    elif not assistant_works:
        print("❌ Assistant integration is not working")
        print("   - Check the confirm_action method")
        print("   - Verify calendar_service.create_event call")
        print("   - Check error handling")

if __name__ == "__main__":
    main() 