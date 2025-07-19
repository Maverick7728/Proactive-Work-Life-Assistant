# 🚀 Setup Guide - Proactive Work-Life Assistant

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for cloning)

## 🛠️ Installation

### 1. Clone or Download the Project

```bash
# If using Git
git clone <repository-url>
cd FREELANCE_ASSISTANT

# Or download and extract the ZIP file
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy the example environment file and configure your settings:

```bash
# Copy example environment file
cp config/env.example .env

# Edit the .env file with your preferences
# Most settings can be left as default for demo purposes
```

## 🎯 Quick Start

### Option 1: Run with Python Script
```bash
python run.py
```

### Option 2: Run with Streamlit Directly
```bash
streamlit run app.py
```

### Option 3: Test the Assistant
```bash
python test_assistant.py
```

## 🌐 Access the Application

Once running, open your web browser and go to:
```
http://localhost:8501
```

## 📱 Features Overview

### 🤖 Core Capabilities

1. **Meeting Scheduling**
   - Natural language meeting requests
   - Automatic availability checking
   - Calendar integration
   - Email invitations

2. **Restaurant Booking**
   - Location-based restaurant search
   - Cuisine preferences
   - Team size accommodation
   - Dinner invitations

3. **Availability Checking**
   - Team member availability
   - Common free time slots
   - Schedule visualization

4. **Email Automation**
   - Professional email generation
   - Bulk invitations
   - Multiple tone options

### 💬 Example Queries

**Meeting Scheduling:**
- "Setup a meeting for Arnav, Yash, and Priyansh on August 10, 2025"
- "Schedule a team meeting tomorrow at 2 PM"
- "Organize a meeting about project planning next Friday"

**Restaurant Booking:**
- "Organize a celebratory team dinner for my 6-person team in Hyderabad next week"
- "Find a restaurant with great Hyderabadi biryani near our Gachibowli office"
- "Book a restaurant for team lunch in Bangalore"

**Availability Checking:**
- "Check availability for John and Sarah on Monday"
- "When is the team free next week?"
- "Find common free time for Arnav, Yash, and Priyansh"

## ⚙️ Configuration

### Environment Variables

The application uses environment variables for configuration. Key settings include:

```bash
# AI Service Configuration
AI_SERVICE=huggingface  # Options: huggingface, cohere, local
AI_MODEL=gpt2
HUGGINGFACE_API_KEY=your_key_here
COHERE_API_KEY=your_key_here

# Calendar Service
CALENDAR_SERVICE=local  # Options: local, google
DEFAULT_MEETING_DURATION=60

# Email Service
EMAIL_SERVICE=console  # Options: smtp, local, console
EMAIL_TONE=professional  # Options: professional, casual, formal

# Location Service
LOCATION_SERVICE=local  # Options: openstreetmap, nominatim, local

# Restaurant Service
RESTAURANT_SERVICE=local  # Options: local, scraping, manual
```

### Free Services Setup

The application is designed to work with free alternatives:

1. **AI Services**: Uses Hugging Face (free tier) or local models
2. **Calendar**: Local SQLite database (no external API needed)
3. **Email**: Console output or local file storage
4. **Location**: OpenStreetMap (free) or local data
5. **Restaurants**: Local database with sample data

## 📁 Project Structure

```
FREELANCE_ASSISTANT/
├── app.py                 # Main Streamlit application
├── run.py                 # Run script
├── test_assistant.py      # Test script
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── SETUP.md              # This setup guide
├── config/               # Configuration files
│   ├── settings.py       # Application settings
│   └── env.example       # Environment variables template
├── src/                  # Source code
│   ├── core/             # Core assistant logic
│   ├── services/         # External service integrations
│   └── utils/            # Utility functions
└── data/                 # Data storage (created automatically)
    ├── users/            # User profiles
    ├── calendar/         # Calendar data
    ├── emails/           # Email storage
    └── restaurants/      # Restaurant database
```

## 🔧 Customization

### Adding Team Members

Edit `src/utils/name_matcher.py` to add your team members:

```python
TEAM_MEMBERS = {
    "arnav": "arnav@company.com",
    "yash": "yash@company.com",
    "priyansh": "priyansh@company.com",
    # Add more team members here
}
```

### Adding Restaurants

The restaurant database is automatically created with sample data. You can add more restaurants by:

1. Editing the default database in `src/services/restaurant_service.py`
2. Using the application interface (if implemented)
3. Manually editing the JSON file in `data/restaurants.json`

### Customizing Email Templates

Email templates can be customized in `src/services/email_service.py`. The application supports different tones:
- Professional
- Casual
- Formal

## 🧪 Testing

### Run Basic Tests
```bash
python test_assistant.py
```

### Test Individual Components
```python
# Test goal parsing
from src.core.goal_parser import GoalParser
parser = GoalParser()
result = parser.parse_goal("Setup a meeting for tomorrow")

# Test calendar service
from src.services.calendar_service import CalendarService
calendar = CalendarService()
events = calendar.get_events(date.today(), date.today())

# Test email service
from src.services.email_service import EmailService
email = EmailService()
success = email.send_email(["test@example.com"], "Test", "Test message")
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're in the correct directory
   - Check that virtual environment is activated
   - Verify all dependencies are installed

2. **Streamlit Not Starting**
   - Check if port 8501 is available
   - Try running `streamlit run app.py --server.port 8502`

3. **Database Errors**
   - Ensure the `data/` directory exists
   - Check file permissions
   - Delete and recreate database files if corrupted

4. **Email Not Sending**
   - Check email service configuration
   - Verify SMTP settings if using SMTP
   - Check console output for local/console modes

### Getting Help

1. Check the console output for error messages
2. Verify all dependencies are installed: `pip list`
3. Test individual components using the test script
4. Check the logs in the application interface

## 🔄 Updates

To update the application:

1. Backup your data directory
2. Pull latest changes (if using Git)
3. Update dependencies: `pip install -r requirements.txt`
4. Restart the application

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the code comments
3. Test with the provided test script
4. Check the Streamlit interface for error messages

## 🎉 Success!

Once everything is set up, you should see:
- A beautiful Streamlit interface
- Working natural language processing
- Calendar integration
- Email automation
- Restaurant booking capabilities

Enjoy your Proactive Work-Life Assistant! 🤖✨ 