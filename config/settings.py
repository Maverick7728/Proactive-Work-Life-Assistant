"""
Application settings and configuration
"""
from dotenv import load_dotenv
import os
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print(f"Warning: .env file not found at {env_path}. Using environment variables from system/Streamlit Cloud.")
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Data directories
DATA_DIR = BASE_DIR / "data"
USERS_DIR = DATA_DIR / "users"
CALENDAR_DIR = DATA_DIR / "calendar"

# Ensure directories exist
USERS_DIR.mkdir(parents=True, exist_ok=True)
CALENDAR_DIR.mkdir(parents=True, exist_ok=True)

# Application settings
APP_NAME = "Proactive Work-Life Assistant"
APP_VERSION = "1.0.0"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# AI Service Configuration
AI_SERVICE = os.getenv("AI_SERVICE", "huggingface")  # huggingface, cohere, local
AI_MODEL = os.getenv("AI_MODEL", "gpt2")  # Default model
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "1000"))
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.7"))

# Calendar Service Configuration
CALENDAR_SERVICE = os.getenv("CALENDAR_SERVICE", "local")  # local, ics, sqlite
DEFAULT_MEETING_DURATION = int(os.getenv("DEFAULT_MEETING_DURATION", "60"))  # minutes
BUFFER_TIME = int(os.getenv("BUFFER_TIME", "15"))  # minutes between meetings
WORKING_HOURS = {
    "start": "09:00",
    "end": "18:00"
}

# Location Service Configuration
LOCATION_SERVICE = os.getenv("LOCATION_SERVICE", "openstreetmap")  # openstreetmap, local, nominatim
DEFAULT_SEARCH_RADIUS = int(os.getenv("DEFAULT_SEARCH_RADIUS", "5000"))  # meters
MAX_RESTAURANT_RESULTS = int(os.getenv("MAX_RESTAURANT_RESULTS", "10"))

# Email Service Configuration
EMAIL_SERVICE = os.getenv("EMAIL_SERVICE", "smtp")  # smtp, local, console
EMAIL_TONE = os.getenv("EMAIL_TONE", "professional")  # professional, casual, formal

# Restaurant Service Configuration
RESTAURANT_SERVICE = os.getenv("RESTAURANT_SERVICE", "api")  # api, local, scraping, manual
RESTAURANT_DB_PATH = os.getenv("RESTAURANT_DB_PATH", str(DATA_DIR / "restaurants.json"))

# API Keys for Restaurant Services
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
OPENTRIPMAP_API_KEY = os.getenv("OPENTRIPMAP_API_KEY", "")
ZOMATO_API_KEY = os.getenv("ZOMATO_API_KEY", "")

# User Interface Settings
REQUIRE_USER_CONFIRMATION = os.getenv("REQUIRE_USER_CONFIRMATION", "True").lower() == "true"
CHECK_USER_CALENDAR = os.getenv("CHECK_USER_CALENDAR", "True").lower() == "true"
TEAM_SIZE_LIMIT = int(os.getenv("TEAM_SIZE_LIMIT", "20"))
MAX_MEETING_ATTENDEES = int(os.getenv("MAX_MEETING_ATTENDEES", "50"))

# File paths
USER_PROFILES_PATH = USERS_DIR / "user_profiles.json"
TEAM_CONTACTS_PATH = USERS_DIR / "team_contacts.json"
CALENDAR_DB_PATH = CALENDAR_DIR / "calendar.db"

# Default values
DEFAULT_TIMEZONE = "Asia/Kolkata"
DEFAULT_LOCATION = "Hyderabad, India"
DEFAULT_CUISINE = "Any"

# Email templates
EMAIL_TEMPLATES = {
    "meeting_invite": {
        "subject_template": "Meeting: {title} - {date} at {time}",
        "body_template": """
Hi {attendees},

I've scheduled a meeting for {date} at {time}.

Meeting Details:
- Title: {title}
- Date: {date}
- Time: {time}
- Duration: {duration} minutes
- Location: {location}

Please let me know if you need to reschedule.

Best regards,
{organizer}
        """
    },
    "dinner_invite": {
        "subject_template": "Team Dinner: {restaurant} on {date}",
        "body_template": """
Hi {attendees},

I've organized a team dinner for {date} at {time}.

Restaurant Details:
- Name: {restaurant}
- Address: {address}
- Cuisine: {cuisine}
- Rating: {rating}

Please confirm your attendance.

Best regards,
{organizer}
        """
    }
}

# Supported date formats
DATE_FORMATS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%d-%m-%Y",
    "%Y/%m/%d",
    "%d %B %Y",  # 18 July 2025
    "%d %b %Y",  # 18 Jul 2025
    "%B %d, %Y", # July 18, 2025
    "%b %d, %Y"  # Jul 18, 2025
]

# Supported time formats
TIME_FORMATS = [
    "%H:%M",
    "%I:%M %p",
    "%I:%M%p"
]

# Common employee name variations
NAME_VARIATIONS = {
    "Manan": ["manan", "Manan", "MANAN"],
    "yash": ["yash", "Yash", "YASH"],
    "priyansh": ["priyansh", "Priyansh", "PRIYANSH"],
    "Nidhi": ["nidhi", "Nidhi", "NIDHI"],
    "Manoj": ["Manoj", "manoj", "MANOJ"],
    "Garv": ["garv", "Garv", "GARV"],
} 