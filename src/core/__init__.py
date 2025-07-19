"""
Core modules for the Proactive Work-Life Assistant
"""
from .assistant import Assistant
from .goal_parser import GoalParser
from .task_planner import TaskPlanner
from .action_executor import ActionExecutor
from .user_manager import UserManager
from .employee_filter import EmployeeFilter
from .confirmation_handler import ConfirmationHandler

__all__ = [
    'Assistant',
    'GoalParser',
    'TaskPlanner',
    'ActionExecutor',
    'UserManager',
    'EmployeeFilter',
    'ConfirmationHandler'
] 