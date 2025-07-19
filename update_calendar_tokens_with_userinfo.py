import os
import json
import requests

TOKEN_PATH = os.path.join('config', 'calendar_token.json')
USERINFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo?alt=json'

with open(TOKEN_PATH, 'r') as f:
    tokens = json.load(f)

updated_tokens = []

for idx, token in enumerate(tokens):
    # Handle both old and new formats
    if 'access_token' in token:
        access_token = token['access_token']
        token_data = token
    elif 'tokens' in token:
        access_token = token['tokens']['access_token']
        token_data = token['tokens']
    else:
        print(f"Token #{idx+1}: No access token found.")
        updated_tokens.append(token)
        continue

    headers = {'Authorization': f'Bearer {access_token}'}
    resp = requests.get(USERINFO_URL, headers=headers)
    if resp.status_code == 200:
        userinfo = resp.json()
        user_email = userinfo.get('email', 'unknown')
        user_name = userinfo.get('name', 'unknown')
        # Store in new format
        updated_tokens.append({
            'user_email': user_email,
            'user_name': user_name,
            'tokens': token_data
        })
        print(f"Token #{idx+1}: {user_email} ({user_name})")
    else:
        print(f"Token #{idx+1}: Failed to fetch user info ({resp.text})")
        updated_tokens.append(token)

with open(TOKEN_PATH, 'w') as f:
    json.dump(updated_tokens, f, indent=2)

print(f"Updated {TOKEN_PATH} with user info.") 