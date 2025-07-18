def handle_google_places_error(error):
    print("[RESTAURANT ERROR] Reason:", str(error))
    print("[FIX] Google Places API error. Check your API key, endpoint, and request payload.")

def handle_opentripmap_error(error):
    print("[RESTAURANT ERROR] Reason:", str(error))
    print("[FIX] OpenTripMap API error. Check your API key, endpoint, and request payload.")

def handle_restaurant_data_error(error):
    print("[RESTAURANT ERROR] Reason:", str(error))
    print("[FIX] Restaurant data error. Check your data source and formatting.")

def handle_unknown_restaurant_error(error):
    print("[RESTAURANT ERROR] Reason:", str(error))
    print("[FIX] An unknown restaurant error occurred. Check your logs and configuration.") 