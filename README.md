# 🤖 Proactive Work-Life Assistant

A smart virtual assistant that elevates from simple command-taking to proactive, goal-oriented task execution by integrating with various real-world services.

## 🎯 Key Features

- **High-Level Goal Interpretation**: Accepts natural language goals instead of specific commands
- **Autonomous Planning**: Breaks goals into logical steps and researches options
- **Multi-Tool Coordination**: Integrates with calendar, location, and email services
- **User Confirmation**: Presents options and gets user approval before actions
- **Employee Filtering**: Only involves the mentioned employees in queries
- **Beautiful UI**: Streamlit-based interface for easy interaction

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Free API keys (optional - works with local alternatives)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment**
```bash
cp .env.example .env
# Edit .env with your API keys (optional - works without them)
```

4. **Run the application**
```bash
python run.py
# or
streamlit run app.py
```

## 📁 Project Structure

```
FREELANCE_ASSISTANT/
├── src/                    # Core application logic
│   ├── core/              # Core modules (assistant, goal parser, etc.)
│   ├── services/          # External service integrations
│   └── utils/             # Utility functions
├── config/                # Configuration files
├── data/                  # User data and storage
├── app.py                 # Streamlit web interface
├── run.py                 # Application launcher
├── test_assistant.py      # Test script
└── requirements.txt       # Python dependencies
```

## 🎯 Example Usage

### Meeting Scheduling
```
User: "Setup a meeting for Nidhi manoj and priyansh on 10 august, 2025"

Assistant: 
1. Extracts names: Nidhi, manoj, priyansh
2. Checks their calendars for July 27, 2025
3. Finds common free time slots
4. Presents options to user
5. Gets confirmation
6. Sends calendar invites only to mentioned employees
```

### Team Dinner
```
User: "Organize a celebratory team dinner for my 6-person team in Hyderabad next week. We want to go somewhere with great Hyderabadi biryani near our Gachibowli office."

Assistant:
1. Searches real restaurants using Google Places, OpenTripMap, and Zomato APIs
2. Finds restaurants with Hyderabadi biryani near Gachibowli
3. Retrieves menu information, ratings, and contact details
4. Checks team availability for next week
5. Presents 2-3 restaurant options with detailed information
6. Gets user confirmation
7. Books the restaurant and sends invites
```

## 🔧 Configuration

### Free API Alternatives Used
- **AI Service**: Hugging Face Inference API (free tier)
- **Calendar**: Local .ics files or SQLite database
- **Location**: OpenStreetMap API (completely free)
- **Email**: SMTP with Gmail/Outlook (free)
- **Restaurants**: Google Places API, OpenTripMap API, Zomato API (all have free tiers)

### Environment Variables
```env
# AI Service
HUGGINGFACE_API_KEY=your_key_here

# Location Service
OPENSTREETMAP_API_KEY=your_key_here

# Restaurant APIs (Free tiers available)
GOOGLE_PLACES_API_KEY=your_google_places_key_here
OPENTRIPMAP_API_KEY=your_opentripmap_key_here
ZOMATO_API_KEY=your_zomato_key_here

# Email Service
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Local Storage
LOCAL_CALENDAR_PATH=./data/calendar/
RESTAURANT_DB_PATH=./data/restaurants.json
```

📖 **For detailed API setup instructions, see [API_SETUP.md](API_SETUP.md)**

## 🧪 Testing

Run tests to ensure everything works correctly:

```bash
python -m pytest tests/
```

