"""
Run script for the Proactive Work-Life Assistant
"""
import subprocess
import sys
import os
# Import error handler modules
from src.errors import gemini_errors, calendar_errors, email_errors, restaurant_errors, location_errors

def main():
    """Run the Streamlit application"""
    print("🚀 Starting Proactive Work-Life Assistant...")
    print("📱 Opening Streamlit interface...")
    
    # Run streamlit app
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Assistant stopped by user")
    except Exception as e:
        # Modular error handling for known error types
        if 'gemini' in str(e).lower():
            gemini_errors.handle_unknown_error(e)
        elif 'calendar' in str(e).lower() or 'sqlite' in str(e).lower():
            calendar_errors.handle_unknown_calendar_error(e)
        elif 'email' in str(e).lower() or 'smtp' in str(e).lower() or 'gmail' in str(e).lower():
            email_errors.handle_unknown_email_error(e)
        elif 'restaurant' in str(e).lower() or 'places' in str(e).lower() or 'opentripmap' in str(e).lower():
            restaurant_errors.handle_unknown_restaurant_error(e)
        elif 'location' in str(e).lower() or 'geocoding' in str(e).lower():
            location_errors.handle_unknown_location_error(e)
        else:
            print(f"❌ Error starting assistant: {e}")
            print("[FIX] An unknown error occurred. Check your logs and configuration.")

if __name__ == "__main__":
    main() 