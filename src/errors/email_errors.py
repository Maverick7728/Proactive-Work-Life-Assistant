def handle_smtp_error(error):
    print("[EMAIL ERROR] Reason:", str(error))
    print("[FIX] SMTP error. Check your SMTP server, credentials, and network connection.")

def handle_gmail_api_error(error):
    print("[EMAIL ERROR] Reason:", str(error))
    print("[FIX] Gmail API error. Check your API key, OAuth credentials, and request payload.")

def handle_email_format_error(error):
    print("[EMAIL ERROR] Reason:", str(error))
    print("[FIX] Email format error. Check your email addresses and message formatting.")

def handle_unknown_email_error(error):
    print("[EMAIL ERROR] Reason:", str(error))
    print("[FIX] An unknown email error occurred. Check your logs and configuration.") 