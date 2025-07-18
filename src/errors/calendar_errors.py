def handle_google_calendar_auth_error(error):
    print("[CALENDAR ERROR] Reason:", str(error))
    print("[FIX] Google Calendar authentication failed. Check your credentials, token file, and API access.")

def handle_google_calendar_api_error(error):
    print("[CALENDAR ERROR] Reason:", str(error))
    print("[FIX] Google Calendar API error. Check your API key, endpoint, and request payload.")

def handle_sqlite_error(error):
    print("[CALENDAR ERROR] Reason:", str(error))
    print("[FIX] SQLite database error. Check your database file, schema, and permissions.")

def handle_unknown_calendar_error(error):
    print("[CALENDAR ERROR] Reason:", str(error))
    print("[FIX] An unknown calendar error occurred. Check your logs and configuration.") 