def handle_geocoding_api_error(error):
    print("[LOCATION ERROR] Reason:", str(error))
    print("[FIX] Geocoding API error. Check your API key, endpoint, and request payload.")

def handle_location_data_error(error):
    print("[LOCATION ERROR] Reason:", str(error))
    print("[FIX] Location data error. Check your data source and formatting.")

def handle_unknown_location_error(error):
    print("[LOCATION ERROR] Reason:", str(error))
    print("[FIX] An unknown location error occurred. Check your logs and configuration.") 