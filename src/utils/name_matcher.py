"""
Name matching utilities for employee filtering
"""
import re
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher
import calendar
from src.utils.validators import validate_email

try:
    from fuzzywuzzy import fuzz, process
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    FUZZYWUZZY_AVAILABLE = False
    print("Warning: fuzzywuzzy not available. Install with: pip install fuzzywuzzy python-Levenshtein")

from config.settings import NAME_VARIATIONS

class NameMatcher:
    """
    Utility class for matching employee names to emails with fuzzy matching
    """
    
    def __init__(self):
        self.team_contacts = self._load_team_contacts()
    
    def _load_team_contacts(self) -> Dict[str, Dict[str, str]]:
        """
        Load team contacts from file
        
        Returns:
            Dictionary of team contacts
        """
        try:
            import json
            from config.settings import TEAM_CONTACTS_PATH, USER_PROFILES_PATH

            team_contacts = {}

            # Load team contacts from team_contacts.json
            if TEAM_CONTACTS_PATH.exists():
                with open(TEAM_CONTACTS_PATH, 'r') as f:
                    data = json.load(f)
                    employees = data.get('employees', [])

                    for employee in employees:
                        name = employee.get('name', '') or ''
                        email = employee.get('email', '') or ''
                        if name and isinstance(name, str):
                            name_lower = name.lower()
                            team_contacts[name_lower] = {
                                'name': employee.get('name', '') or '',
                                'email': email,
                                'full_name': employee.get('name', '') or '',
                                'department': employee.get('department', '') or '',
                                'role': employee.get('role', '') or ''
                            }
                        if email and isinstance(email, str):
                            email_lower = email.lower()
                            team_contacts[email_lower] = {
                                'name': employee.get('name', '') or '',
                                'email': email,
                                'full_name': employee.get('name', '') or '',
                                'department': employee.get('department', '') or '',
                                'role': employee.get('role', '') or ''
                            }

            # Load user profiles from user_profiles.json
            if USER_PROFILES_PATH.exists():
                with open(USER_PROFILES_PATH, 'r') as f:
                    data = json.load(f)
                    users = data.get('users', {})

                    for email, user_info in users.items():
                        name = user_info.get('name', '') or ''
                        if name and isinstance(name, str):
                            name_lower = name.lower()
                            # Use first name as key
                            first_name = name_lower.split()[0] if ' ' in name_lower else name_lower
                            team_contacts[first_name] = {
                                'name': user_info.get('name', '') or '',
                                'email': user_info.get('email', '') or '',
                                'full_name': user_info.get('name', '') or '',
                                'role': user_info.get('role', '') or '',
                                'preferences': user_info.get('preferences', {}) or {}
                            }

            return team_contacts
        except Exception as e:
            print(f"Error loading team contacts: {e}")
            # Return empty dict if loading fails
            return {}
    
    def extract_employee_names(self, user_query: str) -> List[str]:
        """
        Improved: Extract all employee names (including multi-word) from the query, prioritizing exact and multi-word matches.
        """
        query_lower = user_query.lower()
        everyone_keywords = ["everyone", "all employees", "everybody", "all team", "entire team"]
        if any(kw in query_lower for kw in everyone_keywords):
            return [member['name'] for member in self.get_team_members()]

        # Split on common separators
        import re
        separators = [',', ' and ', ' & ']
        segments = [user_query]
        for sep in separators:
            new_segments = []
            for seg in segments:
                new_segments.extend([s.strip() for s in seg.split(sep) if s.strip()])
            segments = new_segments

        matched_names = set()
        team_names = [member['name'] for member in self.get_team_members()]
        # First, try to match multi-word names exactly
        for name in team_names:
            if name.lower() in query_lower:
                matched_names.add(name)
        # Then, try to match each segment to a team member (single-word)
        for seg in segments:
            seg_lower = seg.lower()
            for name in team_names:
                if seg_lower == name.lower():
                    matched_names.add(name)
            # Fuzzy match fallback
            if hasattr(self, '_fuzzy_match_name'):
                best_match = self._fuzzy_match_name(seg_lower)
                if best_match:
                    matched_names.add(self.team_contacts[best_match]['name'])
        if matched_names:
            return list(matched_names)
        return ["__ASK_USER_FOR_EMPLOYEE__"]

    def _fuzzy_match_names(self, query: str) -> List[str]:
        """
        Use fuzzy matching to find employee names in the query
        
        Args:
            query: Lowercase query string
        
        Returns:
            List of matched names
        """
        if not FUZZYWUZZY_AVAILABLE:
            return []
        
        matched_names = []
        team_names = list(self.team_contacts.keys())
        
        # Extract potential name candidates from query
        words = query.split()
        name_candidates = []
        
        # Look for capitalized words (potential names)
        for word in words:
            if len(word) > 2 and word[0].isupper():
                name_candidates.append(word.lower())
        
        # Also look for consecutive capitalized words (full names)
        for i in range(len(words) - 1):
            if (len(words[i]) > 2 and words[i][0].isupper() and 
                len(words[i+1]) > 2 and words[i+1][0].isupper()):
                name_candidates.append(f"{words[i].lower()} {words[i+1].lower()}")
        
        # Fuzzy match each candidate
        for candidate in name_candidates:
            # Use fuzzywuzzy to find best matches
            matches = process.extractBests(
                candidate, 
                team_names, 
                scorer=fuzz.token_sort_ratio,
                score_cutoff=70  # 70% similarity threshold
            )
            
            for match_data in matches:
                if len(match_data) >= 2:
                    match = match_data[0]
                    if match not in matched_names:
                        matched_names.append(match)
        
        return matched_names
    
    def _extract_names_from_text(self, text: str) -> List[str]:
        """
        Extract individual names from text
        
        Args:
            text: Text containing names
        
        Returns:
            List of extracted names
        """
        # Split by common separators
        separators = [',', 'and', '&', 'with', 'for']
        names = [text]
        
        for sep in separators:
            new_names = []
            for name in names:
                if sep in name:
                    parts = name.split(sep)
                    new_names.extend([part.strip() for part in parts if part.strip()])
                else:
                    new_names.append(name)
            names = new_names
        
        return names
    
    def get_emails_for_names(self, names: List[str]) -> List[str]:
        """
        Get email addresses for given names using fuzzy matching
        
        Args:
            names: List of employee names
        
        Returns:
            List of email addresses
        """
        emails = []
        admin_email = None
        for name in names:
            email = self.get_email_for_name(name)
            if email:
                emails.append(email)
        # Always include admin
        if admin_email not in emails:
            emails.append(admin_email)
        return emails
    
    def get_email_for_name(self, name: str) -> Optional[str]:
        """
        Get email address for a specific name or email using fuzzy matching
        Args:
            name: Employee name or email
        Returns:
            Email address or None if not found
        """
        name_lower = name.lower().strip()

        # Direct match by name
        if name_lower in self.team_contacts and self.team_contacts[name_lower].get('email'):
            print(f"[NameMatcher] Direct match for '{name_lower}' -> {self.team_contacts[name_lower]['email']}")
            return self.team_contacts[name_lower]['email']

        # Direct match by email
        for contact in self.team_contacts.values():
            if contact.get('email', '').lower() == name_lower:
                print(f"[NameMatcher] Direct email match for '{name_lower}' -> {contact['email']}")
                return contact['email']

        # First name match (robust)
        for contact in self.team_contacts.values():
            full_name = contact.get('name', '').lower().strip()
            if full_name:
                first_name = full_name.split()[0]
                if name_lower == first_name:
                    print(f"[NameMatcher] First name match for '{name_lower}' -> {contact.get('email')}")
                    return contact.get('email')

        # Fuzzy match (lower threshold for short names)
        threshold = 80 if len(name_lower) > 2 else 60
        best_match = self._fuzzy_match_name(name_lower, threshold=threshold)
        if best_match and self.team_contacts[best_match].get('email'):
            print(f"[NameMatcher] Fuzzy match for '{name_lower}' -> {self.team_contacts[best_match]['email']}")
            return self.team_contacts[best_match]['email']
        print(f"[NameMatcher] No match for '{name_lower}'")
        return None
    
    def _fuzzy_match_name(self, name: str, threshold: int = 80) -> Optional[str]:
        """
        Fuzzy match a name against team contacts using fuzzywuzzy
        
        Args:
            name: Name to match
        
        Returns:
            Best matching name or None
        """
        if not FUZZYWUZZY_AVAILABLE:
            # Fallback to SequenceMatcher
            return self._fuzzy_match_name_fallback(name)
        
        team_names = list(self.team_contacts.keys())
        
        # Use fuzzywuzzy for better matching
        matches = process.extractBests(
            name, 
            team_names, 
            scorer=fuzz.token_sort_ratio,
            score_cutoff=threshold
        )
        
        if matches and len(matches) > 0 and len(matches[0]) > 0:
            return matches[0][0]  # Return the best match
        
        return None
    
    def _fuzzy_match_name_fallback(self, name: str) -> Optional[str]:
        """
        Fallback fuzzy matching using SequenceMatcher
        
        Args:
            name: Name to match
        
        Returns:
            Best matching name or None
        """
        best_ratio = 0
        best_match = None
        
        for contact_name, contact_info in self.team_contacts.items():
            # Check against different name variations
            variations = [
                contact_name,
                contact_info['name'],
                contact_info['full_name']
            ]
            
            for variation in variations:
                ratio = SequenceMatcher(None, name, variation.lower()).ratio()
                if ratio > best_ratio and ratio > 0.8:  # 80% similarity threshold
                    best_ratio = ratio
                    best_match = contact_name
        
        return best_match
    
    def get_team_members(self) -> List[Dict[str, str]]:
        """
        Return all team members as a list of dicts with 'name' and 'email'.
        """
        return [v for v in self.team_contacts.values() if v.get('email')]
    
    def add_team_member(self, name: str, email: str, full_name: Optional[str] = None) -> bool:
        """
        Add a new team member
        
        Args:
            name: Short name
            email: Email address
            full_name: Full name (optional)
        
        Returns:
            True if added successfully, False otherwise
        """
        try:
            self.team_contacts[name.lower()] = {
                'name': name,
                'email': email,
                'full_name': full_name if full_name is not None else name
            }
            
            # Save to file
            self._save_team_contacts()
            return True
        except Exception:
            return False
    
    def remove_team_member(self, name: str) -> bool:
        """
        Remove a team member
        
        Args:
            name: Name of team member to remove
        
        Returns:
            True if removed successfully, False otherwise
        """
        try:
            name_lower = name.lower()
            if name_lower in self.team_contacts:
                del self.team_contacts[name_lower]
                self._save_team_contacts()
                return True
            return False
        except Exception:
            return False
    
    def _save_team_contacts(self):
        """
        Save team contacts to file
        """
        try:
            import json
            from config.settings import TEAM_CONTACTS_PATH
            
            data = {'team_members': self.team_contacts}
            with open(TEAM_CONTACTS_PATH, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
    
    def validate_emails(self, emails: List[str]) -> Dict[str, bool]:
        """
        Validate email addresses
        
        Args:
            emails: List of email addresses
        
        Returns:
            Dictionary mapping emails to validation status
        """
        from .validators import validate_email
        
        results = {}
        for email in emails:
            results[email] = validate_email(email)
        
        return results
    
    def get_missing_emails(self, names: List[str]) -> List[str]:
        """
        Get names that don't have email addresses
        
        Args:
            names: List of names
        
        Returns:
            List of names without emails
        """
        missing = []
        for name in names:
            if not self.get_email_for_name(name):
                missing.append(name)
        
        return missing 

    def _filter_names_and_emails(self, names: List[str]):
        """
        Filter out stopwords, days, ambiguous pronouns, and accept valid emails.
        Returns (filtered_names, valid_emails, warnings)
        """
        stopwords = set([
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'also', 'myself', 'yourself', 'ourselves', 'himself', 'herself', 'itself', 'themselves',
            'someone', 'everyone', 'anyone', 'nobody', 'somebody', 'everybody', 'anybody', 'none',
            'all', 'each', 'other', 'others', 'another', 'such', 'one', 'two', 'three', 'four', 'five',
            'six', 'seven', 'eight', 'nine', 'ten', 'group', 'team', 'member', 'members', 'person', 'people',
            'attendees', 'participant', 'participants', 'guest', 'guests', 'user', 'users', 'employee', 'employees',
            'colleague', 'colleagues', 'friend', 'friends', 'boss', 'manager', 'lead', 'staff', 'crew', 'everyone',
            'some', 'any', 'none', 'who', 'whom', 'whose', 'which', 'that', 'this', 'these', 'those', 'me', 'you', 'us', 'we', 'i', 'he', 'she', 'they', 'it', 'him', 'her', 'them', 'my', 'your', 'our', 'their', 'his', 'hers', 'its', 'theirs', 'your', 'my', 'our', 'their', 'myself', 'yourself', 'ourselves', 'himself', 'herself', 'itself', 'themselves', 'also'
        ])
        days = set(day.lower() for day in list(calendar.day_name) + list(calendar.day_abbr))
        ambiguous_pronouns = set(['her', 'him', 'them', 'also', 'myself', 'yourself', 'ourselves', 'himself', 'herself', 'itself', 'themselves'])
        filtered = []
        emails = []
        warnings = []
        for name in names:
            n = name.strip().lower()
            if n in stopwords or n in days or n in ambiguous_pronouns:
                warnings.append(f"Ignored ambiguous or non-name: '{name}'")
                continue
            if validate_email(name):
                emails.append(name)
                continue
            # If not a valid email, check if it's a known team member
            if not self.get_email_for_name(name):
                warnings.append(f"Unrecognized name or email: '{name}'")
                continue
            filtered.append(name)
        return filtered, emails, warnings 