"""
Task Planner for breaking goals into executable steps
"""
from typing import Dict, Any, List, Optional

class TaskPlanner:
    """
    Planner that breaks high-level goals into executable task plans
    """
    
    def __init__(self):
        self.task_templates = self._load_task_templates()
    
    def _load_task_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load task templates for different goal types"""
        return {
            'meeting': {
                'type': 'meeting_scheduling',
                'steps': [
                    'extract_meeting_details',
                    'check_availability',
                    'find_available_slots',
                    'present_options',
                    'get_confirmation',
                    'schedule_meeting',
                    'send_invites'
                ],
                'required_fields': ['date', 'employees'],
                'optional_fields': ['time', 'duration', 'location', 'title']
            },
            'dinner': {
                'type': 'restaurant_booking',
                'steps': [
                    'extract_restaurant_details',
                    'search_restaurants',
                    'filter_by_criteria',
                    'present_options',
                    'get_confirmation',
                    'book_restaurant',
                    'send_invites'
                ],
                'required_fields': ['location'],
                'optional_fields': ['cuisine', 'date', 'time', 'team_size', 'employees']
            },
            'availability': {
                'type': 'availability_check',
                'steps': [
                    'extract_availability_details',
                    'check_calendars',
                    'find_common_slots',
                    'present_results'
                ],
                'required_fields': ['date', 'employees'],
                'optional_fields': ['time_range']
            },
            'email': {
                'type': 'send_email',
                'steps': [
                    'extract_email_details',
                    'compose_email',
                    'send_email'
                ],
                'required_fields': ['recipients', 'message'],
                'optional_fields': ['subject']
            }
        }
    
    def create_plan(self, goal_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a task plan from goal information
        
        Args:
            goal_info: Parsed goal information
        
        Returns:
            Task plan dictionary or None
        """
        try:
            goal_type = goal_info.get('type')
            
            if goal_type not in self.task_templates:
                return None
            
            template = self.task_templates[goal_type]
            
            # Create task plan
            task_plan = {
                'type': template['type'],
                'steps': template['steps'].copy(),
                'details': goal_info.copy(),
                'current_step': 0,
                'status': 'pending'
            }
            
            # Validate required fields
            validation = self._validate_plan(task_plan)
            if not validation['valid']:
                task_plan['errors'] = validation['errors']
                task_plan['status'] = 'invalid'
            
            return task_plan
            
        except Exception as e:
            print(f"Error creating task plan: {e}")
            return None
    
    def _validate_plan(self, task_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate task plan"""
        goal_type = task_plan['details'].get('type')
        template = self.task_templates.get(goal_type, {})
        
        required_fields = template.get('required_fields', [])
        details = task_plan['details']
        
        errors = []
        for field in required_fields:
            if not details.get(field):
                errors.append(f"Missing required field: {field}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def get_next_step(self, task_plan: Dict[str, Any]) -> Optional[str]:
        """Get the next step in the task plan"""
        steps = task_plan.get('steps', [])
        current_step = task_plan.get('current_step', 0)
        
        if current_step < len(steps):
            return steps[current_step]
        
        return None
    
    def advance_step(self, task_plan: Dict[str, Any]) -> bool:
        """Advance to the next step in the task plan"""
        current_step = task_plan.get('current_step', 0)
        steps = task_plan.get('steps', [])
        
        if current_step < len(steps) - 1:
            task_plan['current_step'] = current_step + 1
            return True
        
        task_plan['status'] = 'completed'
        return False
    
    def update_plan_details(self, task_plan: Dict[str, Any], updates: Dict[str, Any]) -> bool:
        """Update task plan details"""
        try:
            task_plan['details'].update(updates)
            return True
        except Exception as e:
            print(f"Error updating plan details: {e}")
            return False 