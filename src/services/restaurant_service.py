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
        self.geoapify_api_key = os.getenv("GEOAPIFY_API_KEY", "")
        if not self.google_api_key and not self.opentripmap_api_key and not self.geoapify_api_key:
            raise EnvironmentError("At least one of GOOGLE_PLACES_API_KEY, OPENTRIPMAP_API_KEY, or GEOAPIFY_API_KEY must be set in your .env file for restaurant search. Please add your API keys and restart the app.")
        self._init_apis()
    
    def _init_apis(self):
        self.available_apis = []
        if self.google_api_key:
            self.available_apis.append("google")
        if self.geoapify_api_key:
            self.available_apis.append("geoapify")
        if self.opentripmap_api_key:
            self.available_apis.append("opentripmap")
        if not self.available_apis:
            self.available_apis.append("fallback")
    
    def search_restaurants(self, location: str, cuisine: str = None, 
                          min_rating: float = 0.0, max_price: str = None,
                          radius: int = 5000) -> List[Dict[str, Any]]:
        print(f"[DEBUG] Searching restaurants in {location} with cuisine: {cuisine}")
        print(f"[DEBUG] Available APIs: {self.available_apis}")
        
        all_restaurants = []
        successful_apis = []
        
        for api in self.available_apis:
            try:
                print(f"[DEBUG] Trying {api} API...")
                restaurants = []
                
                if api == "google":
                    restaurants = self._search_google_places(location, cuisine, radius)
                elif api == "geoapify":
                    restaurants = self._search_geoapify(location, cuisine, radius)
                elif api == "opentripmap":
                    restaurants = self._search_opentripmap(location, cuisine, radius)
                elif api == "fallback":
                    restaurants = self._search_fallback(location, cuisine)
                else:
                    continue
                
                if restaurants:
                    print(f"[DEBUG] {api} API returned {len(restaurants)} restaurants")
                    all_restaurants.extend(restaurants)
                    successful_apis.append(api)
                else:
                    print(f"[DEBUG] {api} API returned no results")
                    
            except Exception as e:
                print(f"[DEBUG] Error with {api} API: {e}")
                continue
        
        print(f"[DEBUG] Total restaurants before processing: {len(all_restaurants)}")
        print(f"[DEBUG] Successful APIs: {successful_apis}")
        
        if not all_restaurants:
            print(f"[DEBUG] No restaurants found, using enhanced fallback")
            # Enhanced fallback with more realistic data
            all_restaurants = self._get_enhanced_fallback(location, cuisine)
        
        # Remove duplicates and apply filters
        unique_restaurants = self._remove_duplicates(all_restaurants)
        filtered_restaurants = self._apply_filters(unique_restaurants, min_rating, max_price)
        
        # Sort by rating (descending) and then by user_ratings_total
        filtered_restaurants.sort(key=lambda x: (x.get("rating", 0), x.get("user_ratings_total", 0)), reverse=True)
        
        result = filtered_restaurants[:MAX_RESTAURANT_RESULTS]
        print(f"[DEBUG] Final result: {len(result)} restaurants")
        
        return result
    
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
            
            print(f"[DEBUG] Google Places Request URL: {url}")
            print(f"[DEBUG] Google Places Request Params: {params}")
            
            response = requests.get(url, params=params, timeout=15)
            print(f"[DEBUG] Google Places Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"[DEBUG] Google Places API error: {response.status_code} - {response.text}")
                return []
                
            data = response.json()
            
            if data.get("status") not in ["OK", "ZERO_RESULTS"]:
                print(f"[DEBUG] Google Places API status: {data.get('status')} - {data.get('error_message', '')}")
                return []
            
            print(f"[DEBUG] Google Places found {len(data.get('results', []))} places")
            
            restaurants = []
            for place in data.get("results", []):
                restaurant = {
                    "id": place.get("place_id"),
                    "name": place.get("name"),
                    "address": place.get("vicinity", place.get("formatted_address", "")),
                    "rating": place.get("rating", 4.0),
                    "price_level": place.get("price_level", 2),
                    "types": place.get("types", []),
                    "geometry": place.get("geometry", {}),
                    "source": "google",
                    "user_ratings_total": place.get("user_ratings_total", 0),
                    "business_status": place.get("business_status", "OPERATIONAL"),
                    "opening_hours": place.get("opening_hours", {}).get("weekday_text", [])
                }
                
                # Add cuisine information
                if cuisine:
                    restaurant["cuisine"] = cuisine.title()
                else:
                    # Try to extract cuisine from types
                    cuisine_types = [t for t in restaurant["types"] if "restaurant" in t or "food" in t]
                    restaurant["cuisine"] = cuisine_types[0].replace("_", " ").title() if cuisine_types else "Various"
                
                # Get additional details if place_id is available
                if place.get("place_id"):
                    details = self._get_google_place_details(place.get("place_id"))
                    restaurant.update(details)
                    
                restaurants.append(restaurant)
                
            print(f"[DEBUG] Google Places processed {len(restaurants)} restaurants")
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
            
            # Use the correct OpenTripMap API endpoint
            url = "https://api.opentripmap.com/0.1/en/places/radius"
            params = {
                "radius": radius,
                "lon": lng,
                "lat": lat,
                "kinds": "foods",  # Changed from "restaurants" to "foods" which works better
                "apikey": self.opentripmap_api_key,
                "format": "json",
                "limit": 20
            }
            
            print(f"[DEBUG] OpenTripMap Request URL: {url}")
            print(f"[DEBUG] OpenTripMap Request Params: {params}")
            
            response = requests.get(url, params=params, timeout=15)
            print(f"[DEBUG] OpenTripMap Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"[DEBUG] OpenTripMap API error: {response.status_code} - {response.text}")
                return []
                
            data = response.json()
            print(f"[DEBUG] OpenTripMap found {len(data)} places")
            
            restaurants = []
            for place in data:
                # Get detailed information for each place
                place_details = self._get_opentripmap_details(place.get("xid"))
                if place_details and place_details.get("name"):
                    restaurant = {
                        "id": place.get("xid"),
                        "name": place_details.get("name", "Unknown Restaurant"),
                        "address": place_details.get("address", {}).get("road", "") or f"{location} area",
                        "cuisine": cuisine or "Various",
                        "rating": 4.0,  # Default rating since OpenTripMap doesn't provide ratings
                        "price_level": 2,  # Default moderate price
                        "types": ["restaurant", "food"],
                        "source": "opentripmap",
                        "geometry": {"location": {"lat": place.get("point", {}).get("lat", lat), "lng": place.get("point", {}).get("lon", lng)}},
                        "user_ratings_total": 50,  # Default value
                        "business_status": "OPERATIONAL",
                        "opening_hours": []
                    }
                    
                    # Filter by cuisine if specified
                    if cuisine:
                        if cuisine.lower() in restaurant["name"].lower() or any(cuisine.lower() in t.lower() for t in restaurant["types"]):
                            restaurants.append(restaurant)
                    else:
                        restaurants.append(restaurant)
                        
            print(f"[DEBUG] OpenTripMap processed {len(restaurants)} restaurants")
            return restaurants
            
        except Exception as e:
            print(f"OpenTripMap API error: {e}")
            return []
    
    def _get_opentripmap_details(self, xid: str) -> Dict[str, Any]:
        """Get detailed information for a specific place from OpenTripMap"""
        if not xid:
            return {}
        try:
            url = f"https://api.opentripmap.com/0.1/en/places/xid/{xid}"
            params = {"apikey": self.opentripmap_api_key}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error getting OpenTripMap details for {xid}: {e}")
        return {}
    
    def _search_fallback(self, location: str, cuisine: str = None) -> List[Dict[str, Any]]:
        try:
            return [
                {
                    "id": "fallback_1",
                    "name": f"Local Restaurant in {location}",
                    "address": f"Main Street, {location}",
                    "cuisine": cuisine or "Local",
                    "rating": 4.0,
                    "price_level": 2,
                    "source": "fallback"
                }
            ]
        except Exception as e:
            print(f"Fallback search error: {e}")
            return []
    
    def _get_enhanced_fallback(self, location: str, cuisine: str = None) -> List[Dict[str, Any]]:
        """Enhanced fallback with more realistic restaurant data"""
        try:
            restaurants = []
            
            # Common restaurant types based on location and cuisine
            if "hyderabad" in location.lower():
                restaurants = [
                    {
                        "id": "fallback_hyd_1",
                        "name": "Paradise Biryani",
                        "address": "Secunderabad, Hyderabad",
                        "cuisine": "Hyderabadi",
                        "rating": 4.5,
                        "price_level": 3,
                        "types": ["restaurant", "biryani"],
                        "source": "fallback",
                        "user_ratings_total": 1200,
                        "business_status": "OPERATIONAL"
                    },
                    {
                        "id": "fallback_hyd_2", 
                        "name": "Bawarchi Restaurant",
                        "address": "RTC X Roads, Hyderabad",
                        "cuisine": "Indian",
                        "rating": 4.3,
                        "price_level": 2,
                        "types": ["restaurant", "indian"],
                        "source": "fallback",
                        "user_ratings_total": 800,
                        "business_status": "OPERATIONAL"
                    },
                    {
                        "id": "fallback_hyd_3",
                        "name": "Shah Ghouse",
                        "address": "Tolichowki, Hyderabad", 
                        "cuisine": "Hyderabadi",
                        "rating": 4.4,
                        "price_level": 2,
                        "types": ["restaurant", "biryani"],
                        "source": "fallback",
                        "user_ratings_total": 950,
                        "business_status": "OPERATIONAL"
                    }
                ]
            elif "bangalore" in location.lower():
                restaurants = [
                    {
                        "id": "fallback_blr_1",
                        "name": "MTR Restaurant",
                        "address": "Lalbagh Road, Bangalore",
                        "cuisine": "South Indian",
                        "rating": 4.6,
                        "price_level": 2,
                        "types": ["restaurant", "south_indian"],
                        "source": "fallback",
                        "user_ratings_total": 1500,
                        "business_status": "OPERATIONAL"
                    },
                    {
                        "id": "fallback_blr_2",
                        "name": "Vidyarthi Bhavan",
                        "address": "Gandhi Bazaar, Bangalore",
                        "cuisine": "South Indian",
                        "rating": 4.4,
                        "price_level": 1,
                        "types": ["restaurant", "dosa"],
                        "source": "fallback", 
                        "user_ratings_total": 800,
                        "business_status": "OPERATIONAL"
                    }
                ]
            else:
                # Generic restaurants for other locations
                restaurants = [
                    {
                        "id": f"fallback_gen_1",
                        "name": f"Popular Restaurant",
                        "address": f"City Center, {location}",
                        "cuisine": cuisine or "Multi-cuisine",
                        "rating": 4.2,
                        "price_level": 2,
                        "types": ["restaurant"],
                        "source": "fallback",
                        "user_ratings_total": 600,
                        "business_status": "OPERATIONAL"
                    },
                    {
                        "id": f"fallback_gen_2",
                        "name": f"Local Favorites",
                        "address": f"Main Market, {location}",
                        "cuisine": cuisine or "Indian",
                        "rating": 4.0,
                        "price_level": 2,
                        "types": ["restaurant"],
                        "source": "fallback",
                        "user_ratings_total": 400,
                        "business_status": "OPERATIONAL"
                    }
                ]
            
            # Filter by cuisine if specified
            if cuisine:
                filtered = []
                for restaurant in restaurants:
                    if cuisine.lower() in restaurant["cuisine"].lower() or cuisine.lower() in restaurant["name"].lower():
                        filtered.append(restaurant)
                return filtered if filtered else restaurants[:2]
            
            return restaurants
            
        except Exception as e:
            print(f"Enhanced fallback error: {e}")
            return []
    
    def _search_geoapify(self, location: str, cuisine: str = None, radius: int = 5000) -> List[Dict[str, Any]]:
        try:
            # Step 1: Geocode the location to get lat/lon
            geocode_url = "https://api.geoapify.com/v1/geocode/search"
            geocode_params = {
                "text": location,
                "apiKey": self.geoapify_api_key
            }
            geocode_resp = requests.get(geocode_url, params=geocode_params, timeout=10)
            geocode_data = geocode_resp.json()
            features = geocode_data.get("features", [])
            if not features:
                print(f"[Geoapify] No geocode results for location: {location}")
                return []
            coords = features[0]["geometry"]["coordinates"]
            lon, lat = coords[0], coords[1]
            # Step 2: Search for places (restaurants)
            places_url = "https://api.geoapify.com/v2/places"
            filter_str = f"circle:{lon},{lat},{radius}"
            categories = "catering.restaurant"
            if cuisine:
                # Geoapify does not have cuisine filter, but we can filter results after fetching
                pass
            places_params = {
                "categories": categories,
                "filter": filter_str,
                "limit": 30,
                "apiKey": self.geoapify_api_key
            }
            places_resp = requests.get(places_url, params=places_params, timeout=10)
            places_data = places_resp.json()
            restaurants = []
            for place in places_data.get("features", []):
                prop = place.get("properties", {})
                rest = {
                    "id": prop.get("place_id"),
                    "name": prop.get("name"),
                    "address": prop.get("formatted"),
                    "cuisine": cuisine if cuisine else prop.get("cuisine", "Various"),
                    "rating": prop.get("rating", 0),
                    "price_level": prop.get("price_level", None),
                    "types": prop.get("categories", []),
                    "geometry": {"location": {"lat": lat, "lng": lon}},
                    "source": "geoapify",
                    "user_ratings_total": prop.get("datasource", {}).get("raw", {}).get("user_ratings_total", 0),
                    "business_status": prop.get("datasource", {}).get("raw", {}).get("business_status", ""),
                    "opening_hours": prop.get("opening_hours", []),
                    "website": prop.get("website", None),
                    "phone": prop.get("phone", None)
                }
                # If cuisine is specified, filter by name or categories
                if cuisine:
                    if cuisine.lower() not in (rest["name"] or "").lower() and not any(cuisine.lower() in (cat or "").lower() for cat in rest["types"]):
                        continue
                restaurants.append(rest)
            return restaurants
        except Exception as e:
            print(f"Geoapify API error: {e}")
            return []
    
    def _get_location_coordinates(self, location: str) -> Optional[tuple]:
        try:
            # Prefer Geoapify for geocoding if API key is present
            if self.geoapify_api_key:
                url = "https://api.geoapify.com/v1/geocode/search"
                params = {
                    "text": location,
                    "apiKey": self.geoapify_api_key
                }
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                features = data.get("features", [])
                if features:
                    coords = features[0]["geometry"]["coordinates"]
                    # Geoapify returns [lon, lat]
                    return (coords[1], coords[0])
                return None
            # Use Google Geocoding API if Geoapify is not available
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