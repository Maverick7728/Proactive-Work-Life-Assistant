# Configuration Guide

This folder contains all configuration files for the Proactive Work-Life Assistant.

## 📁 File Structure

```
config/
├── README.md                 # This file
├── settings.py              # Main application settings
├── env.example              # Environment variables template
├── cal_token.json           # Google Calendar OAuth tokens (multi-user)
├── gmail_credentials.json   # Gmail API credentials
├── gmail_token.json         # Gmail OAuth token
├── credentials.json         # Google Calendar API credentials
├── token.json              # Legacy Google Calendar token
└── .env                     # Environment variables (create this)
```

## 🔧 Required Configuration Files

### 1. Environment Variables (.env)

Create a `.env` file based on `env.example`:

```bash
# Copy the example file
cp env.example .env

# Edit with your actual values
nano .env
```

**Required Variables:**
```bash
# AI Service (Choose one)
AI_SERVICE=gemini
GEMINI_API_KEY=your_gemini_api_key_here

# Calendar Service
CALENDAR_SERVICE=google
GOOGLE_CALENDAR_TOKEN=config/cal_token.json

# Email Service
EMAIL_SERVICE=gmail
GMAIL_CREDENTIALS=config/gmail_credentials.json
GMAIL_TOKEN=config/gmail_token.json

# Restaurant Services (Optional)
GOOGLE_PLACES_API_KEY=your_google_places_key_here
OPENTRIPMAP_API_KEY=your_opentripmap_key_here
```

### 2. Google Calendar Setup

#### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials

#### Step 2: Download Credentials
1. Download `credentials.json` from Google Cloud Console
2. Place it in the `config/` folder

#### Step 3: Generate OAuth Tokens
Run the setup script:
```bash
python generate_oauth_invites.py
```

This will:
- Create `cal_token.json` with OAuth tokens for all team members
- Send invitation emails to team members for calendar access

### 3. Gmail API Setup (Optional)

#### Step 1: Enable Gmail API
1. In Google Cloud Console, enable Gmail API
2. Create OAuth 2.0 credentials for Gmail

#### Step 2: Download Gmail Credentials
1. Download Gmail credentials as `gmail_credentials.json`
2. Place in `config/` folder

#### Step 3: Generate Gmail Token
```bash
python gmail_oauth_setup.py
```

### 4. Team Contacts Setup

Create `data/users/team_contacts.json`:

```json
{
  "employees": [
    {
      "name": "Arnav Gupta",
      "email": "arnav.gupta.24cse@bmu.edu.in",
      "department": "Engineering",
      "role": "Admin"
    },
    {
      "name": "Bhavya Sharma",
      "email": "bhavya.24cse@bmu.edu.in",
      "department": "Engineering",
      "role": "Developer"
    },
    {
      "name": "Om Patel",
      "email": "om.patel@company.com",
      "department": "Engineering",
      "role": "Developer"
    }
  ]
}
```

## 🚀 Quick Setup Guide

### For New Users:

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd FREELANCE_ASSISTANT
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Cloud Project**
   - Create project in Google Cloud Console
   - Enable Calendar API (and Gmail API if needed)
   - Download credentials

4. **Configure environment**
   ```bash
   cp config/env.example .env
   # Edit .env with your API keys
   ```

5. **Set up team contacts**
   ```bash
   # Create data/users/ directory
   mkdir -p data/users/
   
   # Create team_contacts.json with your team
   nano data/users/team_contacts.json
   ```

6. **Generate OAuth tokens**
   ```bash
   python generate_oauth_invites.py
   ```

7. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 🔑 API Keys Required

### Required:
- **Google Calendar API**: For scheduling meetings
- **Gemini API**: For AI-powered responses

### Optional:
- **Google Places API**: For restaurant search
- **OpenTripMap API**: For location-based restaurant search
- **Gmail API**: For sending emails

## 📝 Configuration Details

### settings.py
Main application configuration with defaults:
- `DEFAULT_TIMEZONE = "Asia/Kolkata"`
- `WORKING_HOURS = {"start": "09:00", "end": "18:00"}`
- `DEFAULT_MEETING_DURATION = 60`

### cal_token.json
Multi-user Google Calendar OAuth tokens:
```json
{
  "user1@company.com": {
    "access_token": "...",
    "refresh_token": "...",
    "scope": ["https://www.googleapis.com/auth/calendar"]
  },
  "user2@company.com": {
    "access_token": "...",
    "refresh_token": "...",
    "scope": ["https://www.googleapis.com/auth/calendar"]
  }
}
```

## 🛠️ Troubleshooting

### Common Issues:

1. **"No token found for user"**
   - Run `python generate_oauth_invites.py` to create tokens
   - Ensure user email is in `cal_token.json`

2. **"API key not found"**
   - Check `.env` file has correct API keys
   - Verify API keys are valid and have proper permissions

3. **"Employee not recognized"**
   - Check `data/users/team_contacts.json` has correct names
   - Ensure names match exactly (case-sensitive)

4. **Timezone issues**
   - Verify `DEFAULT_TIMEZONE = "Asia/Kolkata"` in `settings.py`
   - Check all datetime operations use timezone-aware objects

### Debug Mode:
Enable debug logging in `.env`:
```bash
LOG_LEVEL=DEBUG
```

## 📞 Support

For issues:
1. Check the troubleshooting section above
2. Review logs in the application
3. Verify all configuration files are properly set up
4. Ensure all required APIs are enabled in Google Cloud Console

## 🔒 Security Notes

- Never commit `.env` files to version control
- Keep API keys secure and rotate them regularly
- Use environment variables for sensitive data
- Regularly review OAuth token permissions 