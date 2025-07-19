import os
import json
import requests
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# === CONFIGURATION ===
CLIENT_ID = "808658756810-d64hr9cibginad6cu44jghavmtnrg6l3.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8501/"
TOKEN_URL = "https://oauth2.googleapis.com/token"
TOKEN_PATH = os.path.join("config", "cal_token.json")

# === 1. Ask for user details ===
user_email = input("Enter the user's email address: ").strip()
user_name = input("Enter the user's name: ").strip()

# === 2. Ask for the full redirect URL ===
redirect_url = input("Paste the full redirect URL you received after Google OAuth: ").strip()

# === 3. Extract the code parameter ===
parsed_url = urlparse(redirect_url)
query_params = parse_qs(parsed_url.query)
code = query_params.get("code", [None])[0]

if not code:
    print("Could not find 'code' in the URL. Please check and try again.")
    exit(1)

# === 4. Exchange code for tokens ===
data = {
    "code": code,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": REDIRECT_URI,
    "grant_type": "authorization_code"
}

response = requests.post(TOKEN_URL, data=data)
if response.status_code != 200:
    print("Failed to exchange code for tokens:", response.text)
    exit(1)

tokens = response.json()

# === 5. Prepare token object for this user ===
token_obj = tokens.copy()
token_obj["user_name"] = user_name
# Optionally add timestamp
# token_obj["created_at"] = str(datetime.now())

# === 6. Load or create the multi-user token dict ===
os.makedirs("config", exist_ok=True)
existing_tokens = {}
if os.path.exists(TOKEN_PATH):
    with open(TOKEN_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, dict):
                existing_tokens = data
            elif isinstance(data, list):
                # Convert list to dict if needed
                for entry in data:
                    email = entry.get("user_email")
                    tokens = entry.get("tokens")
                    if email and tokens:
                        existing_tokens[email] = tokens
            else:
                print("Warning: cal_token.json is not a dict or list. Overwriting with new dict.")
        except Exception as e:
            print(f"Error reading cal_token.json: {e}. Overwriting with new dict.")

# === 7. Add or update this user's token ===
existing_tokens[user_email] = token_obj

with open(TOKEN_PATH, "w", encoding="utf-8") as f:
    json.dump(existing_tokens, f, indent=2)

print(f"Tokens for {user_name} ({user_email}) saved to {TOKEN_PATH} in multi-user format.") 