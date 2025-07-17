"""
AI Service for generating email content and processing natural language using Gemini
"""
import os
import json
import requests
from typing import Dict, Any, Optional, List
from config.settings import AI_MAX_TOKENS, AI_TEMPERATURE
from datetime import datetime
from src.errors import gemini_errors

GEMINI_LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../gemini_api.log'))

def log_gemini_api(message: str):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(GEMINI_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")

class AIService:
    """
    AI service for generating email content and processing natural language
    Uses Gemini API for all NLP tasks
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("GEMINI_API_KEY is missing in your .env file. Please add it and restart the app.")
        self.api_url = os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent")
        self.max_tokens = AI_MAX_TOKENS
        self.temperature = AI_TEMPERATURE

    def generate_email_content(self, email_type: str, details: Dict[str, Any]) -> str:
        prompt = self._create_email_prompt(email_type, details)
        return self._generate_with_gemini(prompt)

    def _create_email_prompt(self, email_type: str, details: Dict[str, Any]) -> str:
        if email_type == "meeting_invite":
            return f"""
Generate a professional meeting invitation email with the following details:
- Meeting title: {details.get('title', 'Team Meeting')}
- Date: {details.get('date', 'TBD')}
- Time: {details.get('time', 'TBD')}
- Duration: {details.get('duration', '60')} minutes
- Location: {details.get('location', 'Conference Room')}
- Attendees: {', '.join(details.get('attendees', []))}
- Timezone: Asia/Kolkata (IST)

Please write a professional and concise email invitation. Make sure to use Asia/Kolkata (IST) as the timezone for the meeting time in the email.
            """.strip()
        elif email_type == "dinner_invite":
            return f"""
Generate a casual team dinner invitation email with the following details:
- Restaurant: {details.get('name', 'Restaurant')}
- Date: {details.get('date', 'TBD')}
- Time: {details.get('time', 'TBD')}
- Address: {details.get('address', 'TBD')}
- Cuisine: {details.get('cuisine', 'Various')}
- Rating: {details.get('rating', 'N/A')}/5

Please write a friendly and inviting email.
            """.strip()
        else:
            return f"""
Generate a {email_type} email with the following details:
{json.dumps(details, indent=2)}

Please write a professional email.
            """.strip()

    def _generate_with_gemini(self, prompt: str) -> str:
        try:
            print(f"[DEBUG] Sending request to Gemini API...")
            log_gemini_api(f"[REQUEST] Prompt: {prompt}")
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "maxOutputTokens": self.max_tokens,
                    "temperature": self.temperature
                }
            }
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=10)
            print(f"[DEBUG] Gemini API response status: {response.status_code}")
            log_gemini_api(f"[RESPONSE STATUS] {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                log_gemini_api(f"[RESPONSE DATA] {json.dumps(data)}")
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"]
            else:
                log_gemini_api(f"[ERROR RESPONSE] {response.text}")
            return "[Gemini API did not return a valid response.]"
        except Exception as e:
            log_gemini_api(f"[EXCEPTION] {str(e)}")
            # Use the error handler functions from src/errors/gemini_errors.py
            if isinstance(e, requests.exceptions.Timeout):
                gemini_errors.handle_timeout_error(e)
            elif isinstance(e, requests.exceptions.ConnectionError):
                gemini_errors.handle_connection_error(e)
            elif isinstance(e, requests.exceptions.HTTPError):
                gemini_errors.handle_http_error(e)
            elif isinstance(e, requests.exceptions.RequestException):
                gemini_errors.handle_request_exception(e)
            else:
                gemini_errors.handle_unknown_error(e)
            return f"[Gemini API error: {e}]"

    def process_natural_language(self, query: str) -> Dict[str, Any]:
        prompt = f"Extract the intent and entities from the following user query: '{query}'\nReturn a JSON object with 'intent' and 'entities'."
        result = self._generate_with_gemini(prompt)
        try:
            parsed = json.loads(result)
            return parsed
        except Exception:
            return {"intent": "unknown", "entities": {}, "raw": result}

    def generate_response(self, context: str, user_input: str) -> str:
        prompt = f"Context: {context}\nUser: {user_input}\nAssistant:"
        return self._generate_with_gemini(prompt)

    def summarize_text(self, text: str) -> str:
        prompt = f"Summarize the following text:\n{text}"
        return self._generate_with_gemini(prompt) 