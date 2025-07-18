#!/usr/bin/env python3
"""
Script to generate a new Google Calendar token with full access scope.
"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Paths
CREDENTIALS_PATH = "config/gmail_credentials.json"
TOKEN_PATH = "config/token.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main():
    print("This script will generate a new Google Calendar token with full access.")
    if os.path.exists(TOKEN_PATH):
        print(f"Deleting old token at {TOKEN_PATH}...")
        os.remove(TOKEN_PATH)
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
    creds = flow.run_local_server(port=8501)
    with open(TOKEN_PATH, "w") as token_file:
        token_file.write(creds.to_json())
    print(f"✅ New token saved to {TOKEN_PATH} with scopes: {SCOPES}")

if __name__ == "__main__":
    main() 