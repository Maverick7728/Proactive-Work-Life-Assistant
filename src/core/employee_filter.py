"""
Employee Filter for handling specific employee mentions
"""
from typing import List, Dict, Any, Optional
from src.utils.name_matcher import NameMatcher

class EmployeeFilter:
    """
    Filter for handling specific employee mentions in queries
    """
    
    def __init__(self):
        self.name_matcher = NameMatcher()
    
    def extract_employee_names(self, user_query: str) -> List[str]:
        """
        Extract employee names from user query
        
        Args:
            user_query: User's natural language query
        
        Returns:
            List of extracted employee names
        """
        return self.name_matcher.extract_employee_names(user_query)
    
    def get_emails_for_names(self, names: List[str]) -> List[str]:
        """
        Get email addresses for given names
        
        Args:
            names: List of employee names
        
        Returns:
            List of email addresses
        """
        return self.name_matcher.get_emails_for_names(names)
    
    def filter_employees_by_query(self, user_query: str, all_employees: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter employees based on user query
        
        Args:
            user_query: User's query
            all_employees: List of all available employees
        
        Returns:
            Filtered list of employees
        """
        extracted_names = self.extract_employee_names(user_query)
        
        if not extracted_names:
            return all_employees  # Return all if no specific names mentioned
        
        # Filter employees based on extracted names
        filtered_employees = []
        for employee in all_employees:
            employee_name = employee.get('name', '').lower()
            for extracted_name in extracted_names:
                if extracted_name.lower() in employee_name or employee_name in extracted_name.lower():
                    filtered_employees.append(employee)
                    break
        
        return filtered_employees
    
    def validate_employee_access(self, user_email: str, employee_emails: List[str]) -> Dict[str, Any]:
        """
        Validate if user has access to schedule meetings for specified employees
        
        Args:
            user_email: User's email address
            employee_emails: List of employee emails
        
        Returns:
            Validation results
        """
        # For demo purposes, allow all access
        # In a real implementation, you'd check permissions
        return {
            'valid': True,
            'accessible_employees': employee_emails,
            'restricted_employees': []
        }
    
    def get_employee_details(self, names: List[str]) -> List[Dict[str, Any]]:
        """
        Get detailed information about employees
        
        Args:
            names: List of employee names
        
        Returns:
            List of employee details
        """
        employee_details = []
        
        for name in names:
            email = self.name_matcher.get_email_for_name(name)
            if email:
                employee_details.append({
                    'name': name,
                    'email': email,
                    'available': True
                })
            else:
                employee_details.append({
                    'name': name,
                    'email': None,
                    'available': False
                })
        
        return employee_details
    
    def suggest_employee_names(self, partial_name: str) -> List[str]:
        """
        Suggest employee names based on partial input
        
        Args:
            partial_name: Partial name input
        
        Returns:
            List of suggested names
        """
        team_members = self.name_matcher.get_team_members()
        suggestions = []
        
        partial_lower = partial_name.lower()
        for member in team_members:
            name = member.get('name', '')
            if partial_lower in name.lower():
                suggestions.append(name)
        
        return suggestions[:5]  # Limit to 5 suggestions 