"""
Goal Parser for understanding natural language queries
"""
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, date, timedelta
from src.utils.time_formatter import TimeFormatter
from src.utils.name_matcher import NameMatcher
import json
from config.settings import USER_PROFILES_PATH

try:
    from fuzzywuzzy import fuzz, process
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    FUZZYWUZZY_AVAILABLE = False
    print("Warning: fuzzywuzzy not available. Install with: pip install fuzzywuzzy python-Levenshtein")

class GoalParser:
    """
    Parser for understanding natural language goals and extracting structured information
    """
    
    def __init__(self):
        self.time_formatter = TimeFormatter()
        self.name_matcher = NameMatcher()
        # self.admin_email = None
        # Load admin names from user_profiles.json
        self.admin_names = []
        try:
            with open(USER_PROFILES_PATH, 'r', encoding='utf-8') as f:
                profiles = json.load(f)
                users = profiles.get('users', {})
                for user in users.values():
                    if user.get('is_admin', False):
                        self.admin_names.append(user.get('name'))
        except Exception as e:
            print(f"[GoalParser] Could not load admin names from user_profiles.json: {e}")
        
        # Enhanced patterns for different types of requests
        self.patterns = {
            'meeting': [
                r'setup\s+a\s+meeting',
                r'schedule\s+a\s+meeting',
                r'organize\s+a\s+meeting',
                r'book\s+a\s+meeting',
                r'arrange\s+a\s+meeting',
                r'meeting\s+with',
                r'meeting\s+for',
                r'meeting',
                r'call',
                r'catch up',
                r'1:1',
                r'one on one',
                r'let\'s\s+meet',
                r'can we meet',
                r'find time to meet',
                r'set up a call',
                r'set a meeting',
                r'plan\s+a\s+meeting',
                r'create\s+a\s+meeting',
                r'arrange\s+a\s+call',
            ],
            'dinner': [
                r'organize\s+a\s+dinner',
                r'book\s+a\s+restaurant',
                r'find\s+a\s+restaurant',
                r'team\s+dinner',
                r'celebratory\s+dinner',
                r'dinner\s+for',
                r'find\s+restaurants?',
                r'look for restaurants?',
                r'search for restaurants?',
                r'find.*cuisine',
                r'find.*food',
                r'book\s+a\s+table',
                r'reserve\s+a\s+table',
                r'team\s+lunch',
                r'lunch\s+for',
                r'team\s+meal',
                r'show me .*food',
                r'show me .*restaurant',
                r'show me .*places',
                r'show .*food',
                r'show .*restaurant',
                r'show .*places',
            ],
            'availability': [
                r'check\s+availability',
                r'check\s+calendar',
                r'when\s+is\s+.*\s+free',
                r'find\s+free\s+time',
                r'available\s+time',
                r'when can we meet',
                r'when is.*available',
                r'find.*slot',
                r'find.*availability',
                r'check\s+schedule',
                r'see\s+when.*free',
                r'find\s+open\s+time',
            ],
            'email': [
                r'send an email',
                r'^email ',
                r'^mail ',
                r'greet',
                r'greeting',
                r'congratulate',
                r'convey',
                r'write to',
                r'message ',
                r'inform .* about',
                r'tell .* about',
                r'notify',
                r'let .* know',
                r'update .* about',
                r'announce',
                r'email .* about',
                r'email .* regarding',
                r'email .*',
                r'mail .*',
            ]
        }
    
    def parse_goal(self, user_query: str) -> Optional[Dict[str, Any]]:
        """
        Parse user query to extract goal information
        
        Args:
            user_query: Natural language query from user
        
        Returns:
            Dictionary with parsed goal information or None
        """
        try:
            query_lower = user_query.lower().strip()
            # Debug: print the incoming query
            print(f"[GoalParser] Parsing query: {user_query}")
            # Determine goal type
            goal_type = self._determine_goal_type(query_lower)
            print(f"[GoalParser] Detected goal type: {goal_type}")
            if not goal_type:
                print(f"[GoalParser] No goal type matched for: {user_query}")
                return None
            # Extract details based on goal type
            if goal_type == 'meeting':
                details = self._parse_meeting_goal(user_query, query_lower)
            elif goal_type == 'dinner':
                details = self._parse_dinner_goal(user_query, query_lower)
            elif goal_type == 'availability':
                details = self._parse_availability_goal(user_query, query_lower)
            elif goal_type == 'email':
                details = self._parse_email_goal(user_query, query_lower)
            else:
                print(f"[GoalParser] Unknown goal type: {goal_type}")
                return None
            print(f"[GoalParser] Extracted details: {details}")
            return details
        except Exception as e:
            print(f"Error parsing goal: {e}")
            return None
    
    def _determine_goal_type(self, query: str) -> Optional[str]:
        """Determine the type of goal from the query"""
        for goal_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return goal_type
        return None
    
    def _parse_meeting_goal(self, original_query: str, query_lower: str) -> Dict[str, Any]:
        """Parse meeting-related goals"""
        # Extract and normalize date
        raw_date = self._extract_date(query_lower)
        iso_date = None
        if raw_date:
            parsed_date = self.time_formatter.parse_date(raw_date)
            if parsed_date:
                iso_date = parsed_date.isoformat()
            else:
                iso_date = raw_date  # fallback to raw if parsing fails
        # Clean up employee names
        employees = self._clean_employee_names(self.name_matcher.extract_employee_names(original_query))
        details = {
            'type': 'meeting',
            'title': self._extract_meeting_title(original_query),
            'date': iso_date,
            'time': self._extract_time(query_lower),
            'duration': self._extract_duration(query_lower),
            'location': self._extract_location(query_lower),
            'employees': employees
        }
        # Clean up None values
        details = {k: v for k, v in details.items() if v is not None}
        return details
    
    def _parse_dinner_goal(self, original_query: str, query_lower: str) -> Dict[str, Any]:
        """Parse dinner/restaurant-related goals"""
        raw_date = self._extract_date(query_lower)
        iso_date = None
        if raw_date:
            parsed_date = self.time_formatter.parse_date(raw_date)
            if parsed_date:
                iso_date = parsed_date.isoformat()
            else:
                iso_date = raw_date
        employees = self._clean_employee_names(self.name_matcher.extract_employee_names(original_query))
        location = self._extract_location(query_lower)
        cuisine = self._extract_cuisine(query_lower)
        print(f"[GoalParser] Dinner goal - extracted location: {location}, cuisine: {cuisine}")
        details = {
            'type': 'dinner',
            'location': location,
            'cuisine': cuisine,
            'date': iso_date,
            'time': self._extract_time(query_lower),
            'team_size': self._extract_team_size(query_lower),
            'employees': employees
        }
        details = {k: v for k, v in details.items() if v is not None}
        return details
    
    def _parse_availability_goal(self, original_query: str, query_lower: str) -> Dict[str, Any]:
        """Parse availability checking goals"""
        raw_date = self._extract_date(query_lower)
        iso_date = None
        if raw_date:
            parsed_date = self.time_formatter.parse_date(raw_date)
            if parsed_date:
                iso_date = parsed_date.isoformat()
            else:
                iso_date = raw_date
        employees = self._clean_employee_names(self.name_matcher.extract_employee_names(original_query))
        details = {
            'type': 'availability',
            'date': iso_date,
            'employees': employees
        }
        details = {k: v for k, v in details.items() if v is not None}
        return details
    
    def _parse_email_goal(self, original_query: str, query_lower: str) -> Dict[str, Any]:
        """Parse email-related goals with robust recipient extraction and warnings. Improved to extract appended details as message."""
        # Extract recipients (employee names or emails)
        raw_names = self.name_matcher.extract_employee_names(original_query)
        unmapped = []  # Always initialize
        # Handle special flag for missing recipients
        if raw_names and raw_names[0] == "__ASK_USER_FOR_EMPLOYEE__":
            print("[GoalParser] No recipient found. Prompting user.")
            return {
                'type': 'email',
                'warnings': ['No recipient found. Please specify who to email.'],
                'subject': None,
                'message': original_query
            }
        # If 'everyone' or similar, get all team emails
        if raw_names and set(raw_names) == set([member['name'] for member in self.name_matcher.get_team_members()]):
            recipients = [member['email'] for member in self.name_matcher.get_team_members()]
        else:
            # Map both names and emails to user emails
            recipients = []
            for r in raw_names:
                if '@' in r and self.name_matcher.get_email_for_name(r) is None:
                    from src.utils.validators import validate_email
                    if validate_email(r):
                        recipients.append(r)
                    else:
                        unmapped.append(r)
                else:
                    email = self.name_matcher.get_email_for_name(r)
                    if email:
                        recipients.append(email)
                    else:
                        unmapped.append(r)
        print(f"[GoalParser] Resolved recipients: {recipients}, unmapped: {unmapped}")
        warnings = getattr(self, 'last_employee_warnings', [])
        if unmapped:
            warnings.append(f"Unrecognized recipients: {', '.join(unmapped)}")
        # Try to extract a subject (look for 'about ...', 'regarding ...', etc.)
        subject = None
        subject_patterns = [
            r'about ([^\.]+)',
            r'regarding ([^\.]+)',
            r'to (.+?) (?:about|regarding) ([^\.]+)',
        ]
        for pattern in subject_patterns:
            match = re.search(pattern, query_lower)
            if match:
                subject = match.group(1).strip()
                break
        # Extract message (improved: everything after a colon or as bullet points)
        message = None
        # If the query contains a colon, treat everything after the first colon as the message
        if ':' in original_query:
            message = original_query.split(':', 1)[1].strip()
        else:
            # Fallback to previous patterns
            message_patterns = [
                r'greet(?:ing)?(?: them| [^ ]+)?(?: and [^ ]+)?(?:,? )?(.*)',
                r'inform(?: them| [^ ]+)?(?: and [^ ]+)?(?:,? )?(.*)',
                r'tell(?: them| [^ ]+)?(?: and [^ ]+)?(?:,? )?(.*)',
                r'convey(?: to [^ ]+)?(?:,? )?(.*)',
                r'email(?: to [^ ]+)?(?:,? )?(.*)',
                r'send an email(?: to [^ ]+)?(?:,? )?(.*)',
            ]
            for pattern in message_patterns:
                match = re.search(pattern, query_lower)
                if match and match.group(1).strip():
                    message = match.group(1).strip()
                    break
        # If still no message, fallback to the full query
        if not message:
            message = original_query
        details = {
            'type': 'email',
            'recipients': recipients,
            'subject': subject or 'No Subject',
            'message': message,
        }
        if warnings:
            details['warnings'] = warnings
        details = {k: v for k, v in details.items() if v}
        return details
    
    def _extract_meeting_title(self, query: str) -> Optional[str]:
        """Extract meeting title from query using enhanced patterns and fuzzy matching"""
        # Enhanced meeting title patterns
        patterns = [
            r'meeting\s+(?:about|for|on|regarding)\s+([^,\.]+)',
            r'(?:setup|schedule|organize|plan|create)\s+a\s+meeting\s+(?:about|for|on|regarding)\s+([^,\.]+)',
            r'meeting\s+with\s+.*?\s+(?:about|for|on|regarding)\s+([^,\.]+)',
            r'call\s+(?:about|for|on|regarding)\s+([^,\.]+)',
            r'(?:setup|schedule|organize)\s+a\s+call\s+(?:about|for|on|regarding)\s+([^,\.]+)',
            r'1:1\s+(?:about|for|on|regarding)\s+([^,\.]+)',
            r'one\s+on\s+one\s+(?:about|for|on|regarding)\s+([^,\.]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                if len(title) > 3:  # Avoid very short titles
                    # Clean up the title
                    title = self._clean_meeting_title(title)
                    return title
        
        # Try fuzzy matching for common meeting types
        if FUZZYWUZZY_AVAILABLE:
            common_meeting_types = [
                'project planning', 'status update', 'review', 'discussion',
                'brainstorming', 'planning', 'sync', 'catch up', 'check-in',
                'weekly review', 'monthly review', 'quarterly review',
                'team meeting', 'client meeting', 'stakeholder meeting'
            ]
            
            query_lower = query.lower()
            best_match = self._fuzzy_match_text(query_lower, common_meeting_types, threshold=70)
            if best_match:
                return best_match.title()
        
        return "Team Meeting"  # Default title
    
    def _clean_meeting_title(self, title: str) -> str:
        """Clean and normalize meeting title"""
        # Remove common stop words and clean up
        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        
        words = title.split()
        cleaned_words = [word for word in words if word.lower() not in stop_words]
        
        if cleaned_words:
            return ' '.join(cleaned_words).title()
        
        return title.title()
    
    def _extract_date(self, query: str) -> Optional[str]:
        """Extract date from query"""
        # Expanded date patterns
        date_patterns = [
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}-\d{1,2}-\d{4})',
            r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4})',
            r'(\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4})',
            r'((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4})',
            r'((?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4})',
            r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*,?\s+\d{4})',
            r'(\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december),?\s+\d{4})',
            r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4})',
            r'(\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4})',
            r'((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}\s+\d{4})',
            r'((?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\s+\d{4})'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                print(f"[GoalParser] Date matched: {match.group(1)}")
                return match.group(1)
        # Look for relative dates
        relative_patterns = [
            r'(today)',
            r'(tomorrow)',
            r'(next\s+week)',
            r'(next\s+monday)',
            r'(next\s+friday)',
            r'(this\s+week)',
            r'(next\s+month)'
        ]
        for pattern in relative_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                relative_date = match.group(1).lower()
                parsed_date = self.time_formatter.get_relative_date(relative_date)
                if parsed_date:
                    print(f"[GoalParser] Relative date matched: {relative_date} -> {parsed_date}")
                    return parsed_date.strftime("%Y-%m-%d")
        print(f"[GoalParser] No date matched in: {query}")
        return None
    
    def _extract_time(self, query: str) -> Optional[str]:
        """Extract time from query using enhanced patterns and fuzzy matching"""
        # Enhanced time patterns
        time_patterns = [
            r'(\d{1,2}:\d{2}\s*(?:am|pm)?)',
            r'(\d{1,2}\s*(?:am|pm))',
            r'at\s+(\d{1,2}:\d{2})',
            r'at\s+(\d{1,2}\s*(?:am|pm))',
            r'(\d{1,2}:\d{2})',
            r'(\d{1,2}\s*(?:am|pm))',
            r'(\d{1,2}:\d{2}\s*(?:am|pm))',
            r'(\d{1,2}\s*(?:am|pm))',
            r'(\d{1,2}:\d{2}\s*(?:a\.m\.|p\.m\.))',
            r'(\d{1,2}\s*(?:a\.m\.|p\.m\.))',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                time_str = match.group(1).strip()
                # Normalize time format
                time_str = self._normalize_time_format(time_str)
                return time_str
        
        # Try fuzzy matching for time-related words
        if FUZZYWUZZY_AVAILABLE:
            time_keywords = ['morning', 'afternoon', 'evening', 'night', 'noon', 'midnight']
            query_words = query.lower().split()
            
            for word in query_words:
                matches = process.extractBests(
                    word, 
                    time_keywords, 
                    scorer=fuzz.token_sort_ratio,
                    score_cutoff=80
                )
                if matches:
                    # Convert fuzzy time to specific time
                    fuzzy_time = self._convert_fuzzy_time_to_specific(matches[0][0])
                    if fuzzy_time:
                        return fuzzy_time
        
        return None
    
    def _normalize_time_format(self, time_str: str) -> str:
        """Normalize time string to 24-hour format (e.g., 12:00, 17:00)"""
        import re
        time_str = time_str.lower().strip()
        # Handle am/pm
        match = re.match(r'^(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$', time_str)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            ampm = match.group(3)
            if ampm == 'pm' and hour != 12:
                hour += 12
            if ampm == 'am' and hour == 12:
                hour = 0
            return f"{hour:02d}:{minute:02d}"
        # Already in 24-hour format
        match = re.match(r'^(\d{2}):(\d{2})$', time_str)
        if match:
            return time_str
        # Fallback: noon, midnight
        if time_str in ['noon', '12noon', '12:00noon']:
            return '12:00'
        if time_str in ['midnight', '12midnight', '12:00midnight']:
            return '00:00'
        return time_str
    
    def _convert_fuzzy_time_to_specific(self, fuzzy_time: str) -> Optional[str]:
        """Convert fuzzy time descriptions to specific times"""
        fuzzy_time = fuzzy_time.lower()
        
        time_mappings = {
            'morning': '09:00',
            'afternoon': '14:00',
            'evening': '18:00',
            'night': '20:00',
            'noon': '12:00',
            'midnight': '00:00'
        }
        
        return time_mappings.get(fuzzy_time)
    
    def _fuzzy_match_text(self, text: str, candidates: List[str], threshold: int = 80) -> Optional[str]:
        """
        Use fuzzy matching to find the best match from candidates
        
        Args:
            text: Text to match
            candidates: List of candidate strings
            threshold: Similarity threshold (0-100)
        
        Returns:
            Best matching string or None
        """
        if not FUZZYWUZZY_AVAILABLE:
            return None
        
        matches = process.extractBests(
            text, 
            candidates, 
            scorer=fuzz.token_sort_ratio,
            score_cutoff=threshold
        )
        
        if matches and len(matches) > 0 and len(matches[0]) > 0:
            return matches[0][0]
        
        return None
    
    def _extract_duration(self, query: str) -> Optional[int]:
        """Extract meeting duration from query"""
        duration_patterns = [
            r'(\d+)\s*(?:hour|hr)s?',
            r'(\d+)\s*(?:minute|min)s?',
            r'(\d+)\s*(?:hour|hr)s?\s*(\d+)\s*(?:minute|min)s?'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    # Hours and minutes
                    hours = int(match.group(1))
                    minutes = int(match.group(2))
                    return hours * 60 + minutes
                else:
                    # Just hours or just minutes
                    value = int(match.group(1))
                    if 'hour' in pattern or 'hr' in pattern:
                        return value * 60
                    else:
                        return value
        
        return 60  # Default 1 hour
    
    def _extract_location(self, query: str) -> Optional[str]:
        """Extract location from query, avoiding time expressions as locations."""
        location_patterns = [
            r'in\s+([^,]+)',
            r'at\s+([^,]+)',
            r'near\s+([^,]+)',
            r'around\s+([^,]+)',
            r'location[:\s]+([^,]+)',
            r'venue[:\s]+([^,]+)'
        ]
        time_expressions = [
            r'\b\d{1,2}:\d{2}(?:\s*(?:am|pm))?\b',
            r'\b\d{1,2}\s*(?:am|pm)\b',
            r'\bnoon\b', r'\bmidnight\b', r'\bmorning\b', r'\bevening\b', r'\bafternoon\b', r'\bnight\b'
        ]
        for pattern in location_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Clean up the location
                location = re.sub(r'\s+', ' ', location)
                # Avoid time expressions as locations
                for tpat in time_expressions:
                    if re.search(tpat, location, re.IGNORECASE):
                        location = None
                        break
                if location and len(location) > 2:
                    print(f"[GoalParser] Matched location: {location}")
                    return location
        print(f"[GoalParser] No location matched in: {query}")
        return None
    
    def _extract_cuisine(self, query: str) -> Optional[str]:
        """Extract cuisine type from query"""
        cuisine_keywords = {
            'indian': ['indian', 'curry', 'biryani', 'tandoori'],
            'chinese': ['chinese', 'szechuan', 'cantonese'],
            'italian': ['italian', 'pizza', 'pasta'],
            'mexican': ['mexican', 'taco', 'burrito'],
            'japanese': ['japanese', 'sushi', 'ramen'],
            'thai': ['thai', 'pad thai'],
            'mediterranean': ['mediterranean', 'greek', 'lebanese'],
            'american': ['american', 'burger', 'steak'],
            'hyderabadi': ['hyderabadi', 'biryani', 'haleem']
        }
        
        query_lower = query.lower()
        for cuisine, keywords in cuisine_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return cuisine.title()
        
        return None
    
    def _extract_team_size(self, query: str) -> Optional[int]:
        """Extract team size from query"""
        size_patterns = [
            r'(\d+)\s*person\s*team',
            r'(\d+)\s*people',
            r'team\s+of\s+(\d+)',
            r'(\d+)\s*attendees',
            r'(\d+)\s*members'
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                size = int(match.group(1))
                if 1 <= size <= 50:  # Reasonable team size
                    return size
        
        return None
    
    def validate_goal(self, goal_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parsed goal information
        
        Args:
            goal_info: Parsed goal information
        
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        goal_type = goal_info.get('type')
        
        if goal_type == 'meeting':
            # Validate meeting-specific fields
            if not goal_info.get('date'):
                errors.append("Meeting date is required")
            
            if not goal_info.get('employees'):
                warnings.append("No specific employees mentioned")
        
        elif goal_type == 'dinner':
            # Validate dinner-specific fields
            if not goal_info.get('location'):
                errors.append("Restaurant location is required")
            
            if not goal_info.get('team_size') and not goal_info.get('employees'):
                warnings.append("Team size or specific employees not mentioned")
        
        elif goal_type == 'availability':
            # Validate availability-specific fields
            if not goal_info.get('date'):
                errors.append("Date is required for availability check")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def enhance_goal(self, goal_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance goal information with additional context
        
        Args:
            goal_info: Basic goal information
        
        Returns:
            Enhanced goal information
        """
        enhanced = goal_info.copy()
        
        # Add default values where missing
        if enhanced.get('type') == 'meeting':
            if not enhanced.get('title'):
                enhanced['title'] = 'Team Meeting'
            if not enhanced.get('duration'):
                enhanced['duration'] = 60
            if not enhanced.get('location'):
                enhanced['location'] = 'Conference Room'
        
        elif enhanced.get('type') == 'dinner':
            if not enhanced.get('cuisine'):
                enhanced['cuisine'] = 'Any'
            if not enhanced.get('team_size') and enhanced.get('employees'):
                enhanced['team_size'] = len(enhanced['employees'])
        
        return enhanced 

    def _clean_employee_names(self, names: list) -> list:
        """Remove non-name phrases from employee name extraction results, filter ambiguous, and warn if needed. Always include all valid team member names found in the query, even if they overlap (e.g., 'om' and 'om patel')."""
        # Use NameMatcher's improved filtering
        filtered, emails, warnings = self.name_matcher._filter_names_and_emails(names)
        self.last_employee_warnings = warnings  # Store for later use in parse_goal
        # Always include all valid team member names found in the query
        all_team_names = set(member['name'] for member in self.name_matcher.get_team_members())
        found_names = set()
        for n in names:
            for team_name in all_team_names:
                if team_name.lower() in n.lower() or n.lower() in team_name.lower():
                    found_names.add(team_name)
        return list(found_names) + emails 