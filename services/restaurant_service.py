"""
Restaurant Service for searching and booking restaurants using Google Places and OpenTripMap APIs only
"""
import os
import requests
from typing import List, Dict, Any, Optional
from config.settings import RESTAURANT_SERVICE, MAX_RESTAURANT_RESULTS

class RestaurantService:
    """
    Restaurant service for searching real restaurants using Google Places API and OpenTripMap API only
    """
    
    def __init__(self):
        self.service = RESTAURANT_SERVICE
        self.google_api_key = os.getenv("GOOGLE_PLACES_API_KEY", "")
        self.opentripmap_api_key = os.getenv("OPENTRIPMAP_API_KEY", "")
        if not self.google_api_key and not self.opentripmap_api_key:
            raise EnvironmentError("At least one of GOOGLE_PLACES_API_KEY or OPENTRIPMAP_API_KEY must be set in your .env file for restaurant search. Please add your API keys and restart the app.")
        self._init_apis()
    
    def _init_apis(self):
        self.available_apis = []
        if self.google_api_key:
            self.available_apis.append("google")
        if self.opentripmap_api_key:
            self.available_apis.append("opentripmap")
        if not self.available_apis:
            self.available_apis.append("fallback")
    
    def search_restaurants(self, location: str, cuisine: str = None, 
                          min_rating: float = 0.0, max_price: str = None,
                          radius: int = 5000) -> List[Dict[str, Any]]:
        all_restaurants = []
        for api in self.available_apis:
            try:
                if api == "google":
                    restaurants = self._search_google_places(location, cuisine, radius)
                elif api == "opentripmap":
                    restaurants = self._search_opentripmap(location, cuisine, radius)
                elif api == "fallback":
                    restaurants = self._search_fallback(location, cuisine)
                else:
                    continue
                all_restaurants.extend(restaurants)
            except Exception as e:
                print(f"Error with {api} API: {e}")
                continue
        unique_restaurants = self._remove_duplicates(all_restaurants)
        filtered_restaurants = self._apply_filters(unique_restaurants, min_rating, max_price)
        filtered_restaurants.sort(key=lambda x: x.get("rating", 0), reverse=True)
        return filtered_restaurants[:MAX_RESTAURANT_RESULTS]
    
    def _search_google_places(self, location: str, cuisine: str = None, radius: int = 5000) -> List[Dict[str, Any]]:
        try:
            coords = self._get_location_coordinates(location)
            if not coords:
                print(f"[DEBUG] Could not get coordinates for location: {location}")
                return []
            lat, lng = coords
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": radius,
                "type": "restaurant",
                "key": self.google_api_key
            }
            if cuisine:
                params["keyword"] = cuisine
            print(f"[DEBUG] Google Places API Key: {self.google_api_key}")
            print(f"[DEBUG] Google Places Request URL: {url}")
            print(f"[DEBUG] Google Places Request Params: {params}")
            response = requests.get(url, params=params, timeout=10)
            print(f"[DEBUG] Google Places Raw Response: {response.text}")
            data = response.json()
            restaurants = []
            for place in data.get("results", []):
                restaurant = {
                    "id": place.get("place_id"),
                    "name": place.get("name"),
                    "address": place.get("vicinity"),
                    "rating": place.get("rating", 0),
                    "price_level": place.get("price_level", 0),
                    "types": place.get("types", []),
                    "geometry": place.get("geometry", {}),
                    "source": "google",
                    "user_ratings_total": place.get("user_ratings_total", 0),
                    "business_status": place.get("business_status", ""),
                    "opening_hours": place.get("opening_hours", {}).get("weekday_text", [])
                }
                restaurant.update(self._get_google_place_details(place.get("place_id")))
                restaurants.append(restaurant)
            return restaurants
        except Exception as e:
            print(f"Google Places API error: {e}")
            return []
    
    def _get_google_place_details(self, place_id: str) -> Dict[str, Any]:
        try:
            url = "https://maps.googleapis.com/maps/api/place/details/json"
            params = {
                "place_id": place_id,
                "fields": "formatted_phone_number,opening_hours,website,reviews",
                "key": self.google_api_key
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            result = data.get("result", {})
            return {
                "phone": result.get("formatted_phone_number"),
                "website": result.get("website"),
                "opening_hours": result.get("opening_hours", {}).get("weekday_text", []),
                "reviews": result.get("reviews", [])
            }
        except Exception as e:
            print(f"Error getting place details: {e}")
            return {}
    
    def _search_opentripmap(self, location: str, cuisine: str = None, radius: int = 5000) -> List[Dict[str, Any]]:
        try:
            coords = self._get_location_coordinates(location)
            if not coords:
                print(f"[DEBUG] Could not get coordinates for location: {location}")
                return []
            lat, lng = coords
            url = "https://api.opentripmap.com/0.1/en/places/radius"
            params = {
                "radius": radius,
                "lon": lng,
                "lat": lat,
                "kinds": "restaurants",
                "apikey": self.opentripmap_api_key,
                "limit": 50
            }
            print(f"[DEBUG] OpenTripMap API Key: {self.opentripmap_api_key}")
            print(f"[DEBUG] OpenTripMap Request URL: {url}")
            print(f"[DEBUG] OpenTripMap Request Params: {params}")
            response = requests.get(url, params=params, timeout=10)
            print(f"[DEBUG] OpenTripMap Raw Response: {response.text}")
            data = response.json()
            restaurants = []
            for place in data.get("features", []):
                properties = place.get("properties", {})
                restaurant = {
                    "id": properties.get("xid"),
                    "name": properties.get("name"),
                    "address": properties.get("address", {}).get("road", ""),
                    "cuisine": properties.get("cuisine", ""),
                    "rating": properties.get("rating", 0),
                    "source": "opentripmap",
                    "geometry": place.get("geometry", {})
                }
                restaurants.append(restaurant)
            return restaurants
        except Exception as e:
            print(f"OpenTripMap API error: {e}")
            return []
    
    def _search_fallback(self, location: str, cuisine: str = None) -> List[Dict[str, Any]]:
        try:
            return [
                {
                    "id": "fallback_1",
                    "name": f"Local Restaurant in {location}",
                    "address": f"Main Street, {location}",
                    "cuisine": cuisine or "Local",
                    "rating": 4.0,
                    "price_range": "$$",
                    "source": "fallback"
                }
            ]
        except Exception as e:
            print(f"Fallback search error: {e}")
            return []
    
    def _get_location_coordinates(self, location: str) -> Optional[tuple]:
        try:
            # Use Google Geocoding API instead of Nominatim
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                "address": location,
                "key": self.google_api_key
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            if data.get("status") == "OK" and data.get("results"):
                lat = float(data["results"][0]["geometry"]["location"]["lat"])
                lng = float(data["results"][0]["geometry"]["location"]["lng"])
                return (lat, lng)
            return None
        except Exception as e:
            print(f"Error getting coordinates: {e}")
            return None
    
    def _remove_duplicates(self, restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        unique_restaurants = []
        for restaurant in restaurants:
            key = f"{restaurant.get('name', '')}_{restaurant.get('address', '')}"
            if key not in seen:
                seen.add(key)
                unique_restaurants.append(restaurant)
        return unique_restaurants
    
    def _apply_filters(self, restaurants: List[Dict[str, Any]], min_rating: float, max_price: str) -> List[Dict[str, Any]]:
        filtered = []
        for restaurant in restaurants:
            if restaurant.get("rating", 0) < min_rating:
                continue
            filtered.append(restaurant)
        return filtered
    
    def get_restaurant_recommendations(self, location: str, preferences: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        try:
            restaurants = self.search_restaurants(location)
            if not preferences:
                return restaurants[:5]
            ranked = self._rank_by_preferences(restaurants, preferences)
            return ranked[:5]
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []
    
    def _rank_by_preferences(self, restaurants: List[Dict[str, Any]], preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            for restaurant in restaurants:
                score = 0
                if preferences.get("cuisine") and preferences["cuisine"].lower() in restaurant.get("cuisine", "").lower():
                    score += 10
                if preferences.get("min_rating"):
                    if restaurant.get("rating", 0) >= preferences["min_rating"]:
                        score += 5
                restaurant["preference_score"] = score
            restaurants.sort(key=lambda x: x.get("preference_score", 0), reverse=True)
            return restaurants
        except Exception as e:
            print(f"Error ranking by preferences: {e}")
            return restaurants 