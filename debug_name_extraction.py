#!/usr/bin/env python3
"""
Debug script to test name extraction
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.name_matcher import NameMatcher
from src.core.goal_parser import GoalParser

def debug_name_extraction():
    """Debug the name extraction process"""
    print("🔍 Debugging Name Extraction")
    print("=" * 50)
    
    # Test query
    query = "Check availibility of bhavya on 18 july 2025 and schedule a meeting of bhavya with me"
    
    print(f"Query: {query}")
    print()
    
    # Test NameMatcher directly
    print("1. Testing NameMatcher directly:")
    name_matcher = NameMatcher()
    names = name_matcher.extract_employee_names(query)
    print(f"   Raw extracted names: {names}")
    
    # Test email mapping
    emails = name_matcher.get_emails_for_names(names)
    print(f"   Corresponding emails: {emails}")
    print()
    
    # Test GoalParser
    print("2. Testing GoalParser:")
    goal_parser = GoalParser()
    goal = goal_parser.parse_goal(query)
    print(f"   Goal employees: {goal.get('employees', []) if goal else 'No goal'}")
    print()
    
    # Test the cleaning function
    print("3. Testing _clean_employee_names:")
    cleaned = goal_parser._clean_employee_names(names)
    print(f"   Before cleaning: {names}")
    print(f"   After cleaning: {cleaned}")
    print()
    
    # Test with different queries
    print("4. Testing with different queries:")
    test_queries = [
        "Setup a meeting for bhavya on July 20, 2025",
        "Schedule a call with Priyansh tomorrow",
        "Meeting with Allison about project planning",
        "Check availability for Bhavya and Priyansh on Monday",
    ]
    
    for i, test_query in enumerate(test_queries, 1):
        print(f"   {i}. Query: {test_query}")
        names = name_matcher.extract_employee_names(test_query)
        cleaned = goal_parser._clean_employee_names(names)
        print(f"      Raw: {names}")
        print(f"      Cleaned: {cleaned}")
        print()

if __name__ == "__main__":
    debug_name_extraction() 