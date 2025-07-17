"""
Location Service for geocoding and location-based searches
"""
import os
import requests
import json
from typing import List, Dict, Any, Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from config.settings import LOCATION_SERVICE, DEFAULT_SEARCH_RADIUS

class LocationService:
    """
    Location service for geocoding and location-based searches
    Uses OpenStreetMap and Nominatim as free alternatives
    """
    
    def __init__(self):
        self.service = LOCATION_SERVICE
        self.search_radius = DEFAULT_SEARCH_RADIUS
        
        # Initialize based on service type
        if self.service == "openstreetmap":
            self._init_openstreetmap()
        elif self.service == "nominatim":
            self._init_nominatim()
        elif self.service == "local":
            self._init_local()
    
    def _init_openstreetmap(self):
        """Initialize OpenStreetMap service"""
        self.api_key = os.getenv("OPENSTREETMAP_API_KEY")
        self.base_url = "https://nominatim.openstreetmap.org"
    
    def _init_nominatim(self):
        """Initialize Nominatim geocoding service"""
        self.geolocator = Nominatim(user_agent="proactive_assistant")
    
    def _init_local(self):
        """Initialize local location service"""
        self.local_data = self._load_local_data()
    
    def _load_local_data(self) -> Dict[str, Any]:
        """Load local location data"""
        try:
            # Default location data for common places
            return {
                "hyderabad": {
                    "lat": 17.3850,
                    "lon": 78.4867,
                    "address": "Hyderabad, Telangana, India"
                },
                "gachibowli": {
                    "lat": 17.4401,
                    "lon": 78.3489,
                    "address": "Gachibowli, Hyderabad, Telangana, India"
                },
                "bangalore": {
                    "lat": 12.9716,
                    "lon": 77.5946,
                    "address": "Bangalore, Karnataka, India"
                },
                "mumbai": {
                    "lat": 19.0760,
                    "lon": 72.8777,
                    "address": "Mumbai, Maharashtra, India"
                },
                "delhi": {
                    "lat": 28.7041,
                    "lon": 77.1025,
                    "address": "Delhi, India"
                }
            }
        except Exception:
            return {}
    
    def geocode(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Geocode an address to get coordinates
        
        Args:
            address: Address to geocode
        
        Returns:
            Dictionary with location information or None
        """
        if self.service == "openstreetmap":
            return self._geocode_with_openstreetmap(address)
        elif self.service == "nominatim":
            return self._geocode_with_nominatim(address)
        elif self.service == "local":
            return self._geocode_with_local(address)
        else:
            return None
    
    def _geocode_with_openstreetmap(self, address: str) -> Optional[Dict[str, Any]]:
        """Geocode using OpenStreetMap API"""
        try:
            url = f"{self.base_url}/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1
            }
            
            if self.api_key:
                params['key'] = self.api_key
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    location = data[0]
                    return {
                        'address': location.get('display_name', address),
                        'lat': float(location.get('lat', 0)),
                        'lon': float(location.get('lon', 0)),
                        'type': location.get('type', 'unknown')
                    }
            
            return None
            
        except Exception as e:
            print(f"OpenStreetMap geocoding error: {e}")
            return None
    
    def _geocode_with_nominatim(self, address: str) -> Optional[Dict[str, Any]]:
        """Geocode using Nominatim"""
        try:
            location = self.geolocator.geocode(address)
            
            if location:
                return {
                    'address': location.address,
                    'lat': location.latitude,
                    'lon': location.longitude,
                    'type': 'geocoded'
                }
            
            return None
            
        except Exception as e:
            print(f"Nominatim geocoding error: {e}")
            return None
    
    def _geocode_with_local(self, address: str) -> Optional[Dict[str, Any]]:
        """Geocode using local data"""
        address_lower = address.lower()
        
        for key, data in self.local_data.items():
            if key in address_lower:
                return {
                    'address': data['address'],
                    'lat': data['lat'],
                    'lon': data['lon'],
                    'type': 'local'
                }
        
        return None
    
    def reverse_geocode(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """
        Reverse geocode coordinates to get address
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            Dictionary with address information or None
        """
        if self.service == "nominatim":
            return self._reverse_geocode_with_nominatim(lat, lon)
        elif self.service == "openstreetmap":
            return self._reverse_geocode_with_openstreetmap(lat, lon)
        else:
            return None
    
    def _reverse_geocode_with_nominatim(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Reverse geocode using Nominatim"""
        try:
            location = self.geolocator.reverse(f"{lat}, {lon}")
            
            if location:
                return {
                    'address': location.address,
                    'lat': lat,
                    'lon': lon
                }
            
            return None
            
        except Exception as e:
            print(f"Nominatim reverse geocoding error: {e}")
            return None
    
    def _reverse_geocode_with_openstreetmap(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Reverse geocode using OpenStreetMap"""
        try:
            url = f"{self.base_url}/reverse"
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json'
            }
            
            if self.api_key:
                params['key'] = self.api_key
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'address': data.get('display_name', ''),
                    'lat': lat,
                    'lon': lon
                }
            
            return None
            
        except Exception as e:
            print(f"OpenStreetMap reverse geocoding error: {e}")
            return None
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates
        
        Args:
            lat1: Latitude of first point
            lon1: Longitude of first point
            lat2: Latitude of second point
            lon2: Longitude of second point
        
        Returns:
            Distance in kilometers
        """
        try:
            point1 = (lat1, lon1)
            point2 = (lat2, lon2)
            distance = geodesic(point1, point2).kilometers
            return round(distance, 2)
        except Exception as e:
            print(f"Distance calculation error: {e}")
            return 0.0
    
    def find_nearby_places(self, lat: float, lon: float, radius: float = None, 
                          place_type: str = None) -> List[Dict[str, Any]]:
        """
        Find nearby places using OpenStreetMap
        
        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in meters
            place_type: Type of place to search for
        
        Returns:
            List of nearby places
        """
        if radius is None:
            radius = self.search_radius
        
        try:
            url = f"{self.base_url}/search"
            params = {
                'lat': lat,
                'lon': lon,
                'radius': radius,
                'format': 'json',
                'limit': 10
            }
            
            if place_type:
                params['amenity'] = place_type
            
            if self.api_key:
                params['key'] = self.api_key
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                places = []
                
                for place in data:
                    place_lat = float(place.get('lat', 0))
                    place_lon = float(place.get('lon', 0))
                    
                    places.append({
                        'name': place.get('display_name', ''),
                        'lat': place_lat,
                        'lon': place_lon,
                        'type': place.get('type', 'unknown'),
                        'distance': self.calculate_distance(lat, lon, place_lat, place_lon)
                    })
                
                # Sort by distance
                places.sort(key=lambda x: x['distance'])
                return places
            
            return []
            
        except Exception as e:
            print(f"Nearby places search error: {e}")
            return []
    
    def search_restaurants(self, location: str, cuisine: str = None, 
                          radius: float = None) -> List[Dict[str, Any]]:
        """
        Search for restaurants in a location
        
        Args:
            location: Location to search in
            cuisine: Cuisine type (optional)
            radius: Search radius in meters
        
        Returns:
            List of restaurants
        """
        # First geocode the location
        location_data = self.geocode(location)
        if not location_data:
            return []
        
        # Search for restaurants
        restaurants = self.find_nearby_places(
            location_data['lat'],
            location_data['lon'],
            radius,
            'restaurant'
        )
        
        # Filter by cuisine if specified
        if cuisine:
            restaurants = [
                r for r in restaurants 
                if cuisine.lower() in r['name'].lower()
            ]
        
        return restaurants
    
    def get_location_info(self, address: str) -> Dict[str, Any]:
        """
        Get comprehensive location information
        
        Args:
            address: Address to get info for
        
        Returns:
            Dictionary with location information
        """
        # Geocode the address
        location_data = self.geocode(address)
        
        if not location_data:
            return {
                'address': address,
                'found': False,
                'error': 'Could not geocode address'
            }
        
        # Get nearby places
        nearby_places = self.find_nearby_places(
            location_data['lat'],
            location_data['lon']
        )
        
        return {
            'address': location_data['address'],
            'lat': location_data['lat'],
            'lon': location_data['lon'],
            'found': True,
            'nearby_places': nearby_places[:5],  # Top 5 nearby places
            'service_used': self.service
        }
    
    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """
        Validate coordinate values
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            True if valid, False otherwise
        """
        return -90 <= lat <= 90 and -180 <= lon <= 180
    
    def format_distance(self, distance_km: float) -> str:
        """
        Format distance for display
        
        Args:
            distance_km: Distance in kilometers
        
        Returns:
            Formatted distance string
        """
        if distance_km < 1:
            return f"{int(distance_km * 1000)}m"
        else:
            return f"{distance_km:.1f}km"
    
    def get_directions(self, origin: str, destination: str) -> Optional[Dict[str, Any]]:
        """
        Get directions between two locations (simplified)
        
        Args:
            origin: Origin address
            destination: Destination address
        
        Returns:
            Dictionary with direction information or None
        """
        try:
            # Geocode both locations
            origin_data = self.geocode(origin)
            dest_data = self.geocode(destination)
            
            if not origin_data or not dest_data:
                return None
            
            # Calculate distance
            distance = self.calculate_distance(
                origin_data['lat'], origin_data['lon'],
                dest_data['lat'], dest_data['lon']
            )
            
            return {
                'origin': origin_data,
                'destination': dest_data,
                'distance_km': distance,
                'distance_formatted': self.format_distance(distance)
            }
            
        except Exception as e:
            print(f"Directions error: {e}")
            return None 