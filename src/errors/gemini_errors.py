def handle_timeout_error(error):
    print("[GEMINI ERROR] Reason:", str(error))
    print("[FIX] The Gemini API request timed out. Check your internet connection, firewall, or try increasing the timeout.")

def handle_connection_error(error):
    print("[GEMINI ERROR] Reason:", str(error))
    print("[FIX] Could not connect to Gemini API. Check your internet connection, API URL, and firewall settings.")

def handle_http_error(error):
    print("[GEMINI ERROR] Reason:", str(error))
    print("[FIX] Gemini API returned an HTTP error. Check your API key, endpoint, and request payload.")

def handle_request_exception(error):
    print("[GEMINI ERROR] Reason:", str(error))
    print("[FIX] A requests exception occurred. Check your network and Gemini API configuration.")

def handle_unknown_error(error):
    print("[GEMINI ERROR] Reason:", str(error))
    print("[FIX] An unknown error occurred. Check your Gemini API key, endpoint, and logs for more details.") 