# Complete Setup Guide for Proactive Work-Life Assistant

This guide will walk you through setting up all required API keys and configurations.

## 🚀 Quick Start

1. **Clone the repository**
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Copy environment template**: `cp config/env_template.txt .env`
4. **Follow this guide to get API keys**
5. **Run the application**: `streamlit run app.py`

## 🔑 Required API Keys

### 1. Gemini AI API (Required)

**Purpose**: AI-powered responses and natural language processing

**How to get it**:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key
5. Add to `.env`: `GEMINI_API_KEY=your_key_here`

**Cost**: Free tier available

---

### 2. Google Calendar API (Required)

**Purpose**: Schedule meetings, check availability, manage events

**How to get it**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Calendar API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Download the JSON file as `config/credentials.json`
5. Add to `.env`:
   ```bash
   GOOGLE_CALENDAR_CREDENTIALS=config/credentials.json
   GOOGLE_CALENDAR_TOKEN=config/cal_token.json
   ```

**Cost**: Free

---

### 3. Gmail API (Optional but Recommended)

**Purpose**: Send meeting invites and notifications

**How to get it**:
1. In the same Google Cloud project, enable Gmail API
2. Create OAuth 2.0 credentials for Gmail
3. Download as `config/gmail_credentials.json`
4. Add to `.env`:
   ```bash
   GMAIL_CREDENTIALS=config/gmail_credentials.json
   GMAIL_TOKEN=config/gmail_token.json
   GMAIL_SENDER_EMAIL=your_email@gmail.com
   ```

**Cost**: Free

---

### 4. Google Places API (Optional)

**Purpose**: Restaurant search and location data

**How to get it**:
1. In Google Cloud Console, enable Places API
2. Create API key:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Restrict the key to Places API only
3. Add to `.env`: `GOOGLE_PLACES_API_KEY=your_key_here`

**Cost**: Free tier available

---

### 5. OpenTripMap API (Optional)

**Purpose**: Alternative restaurant and location data

**How to get it**:
1. Go to [OpenTripMap](https://opentripmap.io/)
2. Sign up for free account
3. Get your API key
4. Add to `.env`: `OPENTRIPMAP_API_KEY=your_key_here`

**Cost**: Free tier available

---

## 📋 Step-by-Step Setup

### Step 1: Environment Setup

```bash
# Copy the template
cp config/env_template.txt .env

# Edit with your API keys
nano .env
```

### Step 2: Google Cloud Project Setup

1. **Create Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Click "New Project"
   - Name it (e.g., "Proactive Assistant")
   - Click "Create"

2. **Enable APIs**:
   - Google Calendar API
   - Gmail API (if using email features)
   - Places API (if using restaurant search)

3. **Create Credentials**:
   - OAuth 2.0 Client ID for Calendar
   - OAuth 2.0 Client ID for Gmail
   - API Key for Places (if needed)

### Step 3: Team Configuration

Create `data/users/team_contacts.json`:

```json
{
  "employees": [
    {
      "name": "Your Name",
      "email": "your.email@company.com",
      "department": "Engineering",
      "role": "Admin"
    },
    {
      "name": "Team Member 1",
      "email": "member1@company.com",
      "department": "Engineering",
      "role": "Developer"
    }
  ]
}
```

### Step 4: Generate OAuth Tokens

```bash
# Generate calendar tokens for all team members
python generate_oauth_invites.py

# Generate Gmail token (if using Gmail)
python gmail_oauth_setup.py
```

### Step 5: Test Configuration

```bash
# Test all API connections
python test/test_api_connections.py

# Run the application
streamlit run app.py
```

## 🔧 Configuration Options

### AI Service Options

Choose one in `.env`:
- `AI_SERVICE=gemini` (Recommended)
- `AI_SERVICE=huggingface`
- `AI_SERVICE=cohere`
- `AI_SERVICE=local`

### Calendar Service Options

Choose one in `.env`:
- `CALENDAR_SERVICE=google` (Recommended)
- `CALENDAR_SERVICE=local`
- `CALENDAR_SERVICE=ics`

### Email Service Options

Choose one in `.env`:
- `EMAIL_SERVICE=gmail` (Recommended)
- `EMAIL_SERVICE=smtp`
- `EMAIL_SERVICE=local`
- `EMAIL_SERVICE=console`

## 🛠️ Troubleshooting

### Common Issues

1. **"No module named 'google'"**
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

2. **"Invalid API key"**
   - Check API key is correct
   - Ensure API is enabled in Google Cloud Console
   - Verify key restrictions allow your usage

3. **"OAuth consent screen not configured"**
   - Go to Google Cloud Console > APIs & Services > OAuth consent screen
   - Configure consent screen
   - Add test users if in testing mode

4. **"Calendar access denied"**
   - Run `python generate_oauth_invites.py`
   - Accept calendar access for all team members
   - Check `cal_token.json` has all user tokens

### Debug Mode

Enable debug logging in `.env`:
```bash
LOG_LEVEL=DEBUG
```

## 💰 Cost Estimation

**Free Tier (Recommended)**:
- Gemini AI: Free tier available
- Google Calendar: Free
- Gmail API: Free
- Google Places: $200 free credit/month
- OpenTripMap: Free tier available

**Total**: $0-10/month for typical usage

## 🔒 Security Best Practices

1. **Never commit `.env` files**
2. **Use environment variables**
3. **Restrict API keys** to specific services
4. **Regularly rotate keys**
5. **Monitor API usage**

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review application logs
3. Verify all API keys are correct
4. Ensure all required APIs are enabled

## 🎯 Next Steps

After setup:
1. Test basic functionality
2. Configure team contacts
3. Set up working hours
4. Customize email templates
5. Test meeting scheduling 