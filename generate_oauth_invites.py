import json
from src.services.ai_service import AIService
from src.services.email_service import EmailService
from urllib.parse import urlencode
import os
from dotenv import load_dotenv
load_dotenv(os.path.join('config', '.env'))

# Ask the user for their name to use as the sender
sender_name = input("Enter your name to use as the sender in the emails: ").strip()

# Load team contacts (adjust path if needed)
with open('data/users/team_contacts.json', 'r') as f:
    team_contacts = json.load(f)["employees"]

# Google OAuth details (update as needed)
CLIENT_ID = "808658756810-d64hr9cibginad6cu44jghavmtnrg6l3.apps.googleusercontent.com"
REDIRECT_URI = "http://localhost:8501/"
SCOPE = "https://www.googleapis.com/auth/calendar"
OAUTH_URL = (
    "https://accounts.google.com/o/oauth2/v2/auth?"
    + urlencode({
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent"
    })
)

# Initialize services
ai_service = AIService()
email_service = EmailService()

for member in team_contacts:
    name = member.get("name")
    email = member.get("email")
    if not email:
        continue

    # Prepare a detailed prompt for Gemini to use the user's name as sender
    prompt = (
        f"Write a short, clear, friendly email to {name} asking them to authorize access to their Google Calendar for our team assistant project. "
        f"Explain that this is needed so the assistant can help schedule meetings and check availability. "
        f"Include this direct authorization link: {OAUTH_URL}. "
        f"Sign the email as {sender_name}. Do not use any placeholders."
    )
    subject = "Please authorize calendar access for the team assistant"
    body = ai_service._generate_with_gemini(prompt)

    # Print for review
    print("="*60)
    print(f"To: {email}")
    print(f"Subject: {subject}")
    print("Body:")
    print(body)
    print("="*60)
    print("\n")

    # Ask for consent to send
    consent = input(f"Send this email to {name} ({email})? (yes/no): ").strip().lower()
    if consent == "yes":
        email_service.send_email([email], subject, body)
        print(f"Email sent to {name} ({email}).\n")
    else:
        print(f"Skipped sending email to {name} ({email}).\n")

print("All invitation emails have been processed.") 