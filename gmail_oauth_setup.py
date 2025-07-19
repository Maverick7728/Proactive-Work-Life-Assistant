from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
creds_path = 'config/gmail_credentials.json'
token_path = 'config/gmail_token.json'

if not os.path.exists(creds_path):
    raise FileNotFoundError(f'Gmail credentials file not found at {creds_path}')

flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
creds = flow.run_local_server(port=8501)

# Save the credentials for the next run
with open(token_path, 'w') as token:
    token.write(creds.to_json())

print(f'Token saved to {token_path}') 