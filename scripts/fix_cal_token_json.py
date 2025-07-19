import json
import os

TOKEN_PATH = 'config/cal_token.json'


def fix_cal_token_json(token_path=TOKEN_PATH):
    if not os.path.exists(token_path):
        print(f"File not found: {token_path}")
        return
    with open(token_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # If already a dict, do nothing
    if isinstance(data, dict):
        print("cal_token.json is already in the correct format.")
        return
    # If it's a list, convert to dict
    if isinstance(data, list):
        fixed = {}
        for entry in data:
            email = entry.get('user_email')
            tokens = entry.get('tokens')
            if email and tokens:
                fixed[email] = tokens
            else:
                print(f"Skipping entry (missing email or tokens): {entry}")
        with open(token_path, 'w', encoding='utf-8') as f:
            json.dump(fixed, f, indent=2)
        print(f"Fixed cal_token.json. Converted {len(fixed)} users.")
    else:
        print("cal_token.json is not a list or dict. Please check the file format.")

if __name__ == "__main__":
    fix_cal_token_json() 