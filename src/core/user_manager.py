"""
User Manager for handling user data and preferences
"""
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from config.settings import USER_PROFILES_PATH

class UserManager:
    """
    Manager for handling user data, preferences, and profiles
    """
    
    def __init__(self):
        self.profiles_path = Path(USER_PROFILES_PATH)
        self.profiles_path.parent.mkdir(parents=True, exist_ok=True)
        self.user_profiles = self._load_user_profiles()
    
    def _load_user_profiles(self) -> Dict[str, Any]:
        """Load user profiles from file"""
        try:
            if self.profiles_path.exists():
                with open(self.profiles_path, 'r') as f:
                    return json.load(f)
            else:
                # Create default profiles
                default_profiles = self._create_default_profiles()
                self._save_user_profiles(default_profiles)
                return default_profiles
        except Exception as e:
            print(f"Error loading user profiles: {e}")
            return self._create_default_profiles()
    
    def _create_default_profiles(self) -> Dict[str, Any]:
        """Create default user profiles"""
        return {
            "users": {
                "admin@company.com": {
                    "name": "Admin User",
                    "email": "admin@company.com",
                    "role": "admin",
                    "preferences": {
                        "default_meeting_duration": 60,
                        "default_location": "Conference Room",
                        "email_tone": "professional",
                        "timezone": "UTC"
                    }
                }
            }
        }
    
    def _save_user_profiles(self, profiles: Dict[str, Any]):
        """Save user profiles to file"""
        try:
            with open(self.profiles_path, 'w') as f:
                json.dump(profiles, f, indent=2)
        except Exception as e:
            print(f"Error saving user profiles: {e}")
    
    def get_user_profile(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile by email
        
        Args:
            email: User's email address
        
        Returns:
            User profile or None
        """
        return self.user_profiles.get("users", {}).get(email)
    
    def create_user_profile(self, email: str, name: str, role: str = "user",
                          preferences: Dict[str, Any] = None) -> bool:
        """
        Create a new user profile
        
        Args:
            email: User's email address
            name: User's name
            role: User's role
            preferences: User preferences
        
        Returns:
            True if created successfully, False otherwise
        """
        try:
            if email in self.user_profiles.get("users", {}):
                return False  # User already exists
            
            user_profile = {
                "name": name,
                "email": email,
                "role": role,
                "preferences": preferences or {}
            }
            
            self.user_profiles["users"][email] = user_profile
            self._save_user_profiles(self.user_profiles)
            
            return True
            
        except Exception as e:
            print(f"Error creating user profile: {e}")
            return False
    
    def update_user_profile(self, email: str, updates: Dict[str, Any]) -> bool:
        """
        Update user profile
        
        Args:
            email: User's email address
            updates: Profile updates
        
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            if email not in self.user_profiles.get("users", {}):
                return False
            
            user_profile = self.user_profiles["users"][email]
            user_profile.update(updates)
            
            self._save_user_profiles(self.user_profiles)
            return True
            
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False
    
    def delete_user_profile(self, email: str) -> bool:
        """
        Delete user profile
        
        Args:
            email: User's email address
        
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if email not in self.user_profiles.get("users", {}):
                return False
            
            del self.user_profiles["users"][email]
            self._save_user_profiles(self.user_profiles)
            
            return True
            
        except Exception as e:
            print(f"Error deleting user profile: {e}")
            return False
    
    def get_user_preferences(self, email: str) -> Dict[str, Any]:
        """
        Get user preferences
        
        Args:
            email: User's email address
        
        Returns:
            User preferences dictionary
        """
        user_profile = self.get_user_profile(email)
        if user_profile:
            return user_profile.get("preferences", {})
        return {}
    
    def update_user_preferences(self, email: str, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences
        
        Args:
            email: User's email address
            preferences: New preferences
        
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            if email not in self.user_profiles.get("users", {}):
                return False
            
            user_profile = self.user_profiles["users"][email]
            current_preferences = user_profile.get("preferences", {})
            current_preferences.update(preferences)
            user_profile["preferences"] = current_preferences
            
            self._save_user_profiles(self.user_profiles)
            return True
            
        except Exception as e:
            print(f"Error updating user preferences: {e}")
            return False
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Get all user profiles
        
        Returns:
            List of user profiles
        """
        users = self.user_profiles.get("users", {})
        return [
            {
                "email": email,
                "name": profile.get("name", ""),
                "role": profile.get("role", "user")
            }
            for email, profile in users.items()
        ]
    
    def validate_user(self, email: str) -> bool:
        """
        Validate if user exists
        
        Args:
            email: User's email address
        
        Returns:
            True if user exists, False otherwise
        """
        return email in self.user_profiles.get("users", {})
    
    def get_user_role(self, email: str) -> str:
        """
        Get user role
        
        Args:
            email: User's email address
        
        Returns:
            User role
        """
        user_profile = self.get_user_profile(email)
        if user_profile:
            return user_profile.get("role", "user")
        return "user" 

    def get_user_profile_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile by name (case-insensitive)
        Args:
            name: User's name
        Returns:
            User profile or None
        """
        name_lower = name.lower().strip()
        for profile in self.user_profiles.get("users", {}).values():
            if profile.get("name", "").lower().strip() == name_lower:
                return profile
        return None

    def get_email_by_name(self, name: str) -> Optional[str]:
        profile = self.get_user_profile_by_name(name)
        if profile:
            return profile.get("email")
        return None

    def get_name_by_email(self, email: str) -> Optional[str]:
        profile = self.get_user_profile(email)
        if profile:
            return profile.get("name")
        return None 