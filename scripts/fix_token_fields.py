import json
import os

TOKEN_PATH = 'config/cal_token.json'
CLIENT_ID = "1094157793103-ikj9ru7uj9b192076chljfhi8v615405.apps.googleusercontent.com"
CLIENT_SECRET = "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"
TOKEN_URI = "https://oauth2.googleapis.com/token"


def fix_token_fields(token_path=TOKEN_PATH):
    if not os.path.exists(token_path):
        print(f"File not found: {token_path}")
        return
    with open(token_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, dict):
        print("cal_token.json is not a dict. Please fix the format first.")
        return
    changed = 0
    for email, token in data.items():
        updated = False
        if 'client_id' not in token:
            token['client_id'] = CLIENT_ID
            updated = True
        if 'client_secret' not in token:
            token['client_secret'] = CLIENT_SECRET
            updated = True
        if 'token_uri' not in token:
            token['token_uri'] = TOKEN_URI
            updated = True
        if updated:
            changed += 1
            print(f"Updated fields for {email}")
    if changed > 0:
        with open(token_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Added missing fields to {changed} user(s) in {token_path}.")
    else:
        print("All user tokens already have required fields.")

if __name__ == "__main__":
    fix_token_fields() 