"""
Confirmation Handler for managing user confirmations
"""
from typing import Dict, Any, List, Optional
from src.utils.formatters import format_confirmation_message

class ConfirmationHandler:
    """
    Handler for managing user confirmations and approvals
    """
    
    def __init__(self):
        self.pending_confirmations = {}
        self.confirmation_counter = 0
    
    def create_confirmation(self, action_type: str, action_details: Dict[str, Any],
                          user_email: str = None) -> Dict[str, Any]:
        """
        Create a confirmation request
        
        Args:
            action_type: Type of action to confirm
            action_details: Details of the action
            user_email: User's email address
        
        Returns:
            Confirmation request details
        """
        self.confirmation_counter += 1
        confirmation_id = f"conf_{self.confirmation_counter}"
        
        confirmation = {
            'id': confirmation_id,
            'action_type': action_type,
            'action_details': action_details,
            'user_email': user_email,
            'status': 'pending',
            'created_at': '2024-01-01T00:00:00Z'  # In real implementation, use datetime
        }
        
        self.pending_confirmations[confirmation_id] = confirmation
        
        return confirmation
    
    def get_confirmation_message(self, confirmation: Dict[str, Any]) -> str:
        """
        Generate confirmation message for user
        
        Args:
            confirmation: Confirmation details
        
        Returns:
            Formatted confirmation message
        """
        action_type = confirmation.get('action_type')
        action_details = confirmation.get('action_details', {})
        
        return format_confirmation_message(action_type, action_details)
    
    def process_confirmation(self, confirmation_id: str, user_response: str) -> Dict[str, Any]:
        """
        Process user confirmation response
        
        Args:
            confirmation_id: Confirmation ID
            user_response: User's response (yes/no/confirm/cancel)
        
        Returns:
            Processing results
        """
        if confirmation_id not in self.pending_confirmations:
            return {
                'success': False,
                'message': 'Confirmation not found',
                'error': 'confirmation_not_found'
            }
        
        confirmation = self.pending_confirmations[confirmation_id]
        response_lower = user_response.lower().strip()
        
        # Check if user confirmed
        if response_lower in ['yes', 'confirm', 'ok', 'proceed', 'sure']:
            confirmation['status'] = 'confirmed'
            confirmation['user_response'] = user_response
            
            return {
                'success': True,
                'message': 'Action confirmed. Proceeding with execution.',
                'status': 'confirmed',
                'action_type': confirmation['action_type'],
                'action_details': confirmation['action_details']
            }
        
        elif response_lower in ['no', 'cancel', 'abort', 'stop']:
            confirmation['status'] = 'cancelled'
            confirmation['user_response'] = user_response
            
            return {
                'success': True,
                'message': 'Action cancelled by user.',
                'status': 'cancelled'
            }
        
        else:
            return {
                'success': False,
                'message': 'Please respond with "yes" to confirm or "no" to cancel.',
                'status': 'pending'
            }
    
    def get_pending_confirmations(self, user_email: str = None) -> List[Dict[str, Any]]:
        """
        Get pending confirmations for a user
        
        Args:
            user_email: User's email address (optional)
        
        Returns:
            List of pending confirmations
        """
        pending = []
        
        for confirmation in self.pending_confirmations.values():
            if confirmation['status'] == 'pending':
                if user_email is None or confirmation.get('user_email') == user_email:
                    pending.append(confirmation)
        
        return pending
    
    def clear_confirmation(self, confirmation_id: str) -> bool:
        """
        Clear a confirmation from pending list
        
        Args:
            confirmation_id: Confirmation ID
        
        Returns:
            True if cleared successfully, False otherwise
        """
        if confirmation_id in self.pending_confirmations:
            del self.pending_confirmations[confirmation_id]
            return True
        return False
    
    def clear_expired_confirmations(self, max_age_hours: int = 24) -> int:
        """
        Clear expired confirmations
        
        Args:
            max_age_hours: Maximum age in hours
        
        Returns:
            Number of confirmations cleared
        """
        # In a real implementation, you'd check actual timestamps
        # For demo purposes, we'll just clear old confirmations
        cleared_count = 0
        
        for confirmation_id in list(self.pending_confirmations.keys()):
            confirmation = self.pending_confirmations[confirmation_id]
            if confirmation['status'] in ['confirmed', 'cancelled']:
                del self.pending_confirmations[confirmation_id]
                cleared_count += 1
        
        return cleared_count
    
    def get_confirmation_status(self, confirmation_id: str) -> Optional[str]:
        """
        Get status of a confirmation
        
        Args:
            confirmation_id: Confirmation ID
        
        Returns:
            Confirmation status or None
        """
        if confirmation_id in self.pending_confirmations:
            return self.pending_confirmations[confirmation_id]['status']
        return None 