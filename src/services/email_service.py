"""
Email Service for sending automated emails
"""
import os
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from datetime import datetime
from config.settings import EMAIL_SERVICE, EMAIL_TONE

# Gmail API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    import base64
    from email.mime.text import MIMEText
    from google.auth.transport.requests import Request
    GMAIL_API_AVAILABLE = True
except ImportError:
    GMAIL_API_AVAILABLE = False

GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class EmailService:
    """
    Email service for sending automated emails
    Uses SMTP with Gmail/Outlook, Gmail API, or local/console as alternatives
    """
    
    def __init__(self):
        self.service = EMAIL_SERVICE
        self.tone = EMAIL_TONE
        self.gmail_creds = None
        self.gmail_service = None
        if self.service == "gmail" and GMAIL_API_AVAILABLE:
            self._init_gmail()
        elif self.service == "smtp":
            self._init_smtp()
        elif self.service == "local":
            self._init_local()
        elif self.service == "console":
            self._init_console()
    
    def _init_smtp(self):
        self.smtp_email = os.getenv("SMTP_EMAIL")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        if not self.smtp_email or not self.smtp_password:
            raise EnvironmentError("SMTP_EMAIL and/or SMTP_PASSWORD are missing in your .env file. Please add them and restart the app.")
    
    def _init_local(self):
        """Initialize local email service (save to files)"""
        self.email_dir = "data/emails"
        os.makedirs(self.email_dir, exist_ok=True)
    
    def _init_console(self):
        """Initialize console email service (print to console)"""
        pass

    def _init_gmail(self):
        creds_path = os.getenv("GMAIL_CREDENTIALS", "config/gmail_credentials.json")
        token_path = os.getenv("GMAIL_TOKEN", "config/gmail_token.json")
        if not os.path.exists(creds_path):
            raise EnvironmentError(f"GMAIL_CREDENTIALS file not found at {creds_path}. Please provide your Gmail API credentials.")
        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, GMAIL_SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, GMAIL_SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        self.gmail_creds = creds
        self.gmail_service = build('gmail', 'v1', credentials=creds)
    
    def send_email(self, to_emails: List[str], subject: str, content: str, from_email: str = None, cc_emails: List[str] = None) -> bool:
        if self.service == "gmail" and self.gmail_service:
            return self._send_with_gmail(to_emails, subject, content, from_email, cc_emails)
        elif self.service == "smtp":
            return self._send_with_smtp(to_emails, subject, content, from_email, cc_emails)
        elif self.service == "local":
            return self._send_with_local(to_emails, subject, content, from_email, cc_emails)
        elif self.service == "console":
            return self._send_with_console(to_emails, subject, content, from_email, cc_emails)
        else:
            return False
    
    def _send_with_smtp(self, to_emails: List[str], subject: str, content: str,
                       from_email: str = None, cc_emails: List[str] = None) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email or self.smtp_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # Add body
            msg.attach(MIMEText(content, 'plain'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_email, self.smtp_password)
            
            # Send email
            all_recipients = to_emails + (cc_emails or [])
            server.sendmail(self.smtp_email, all_recipients, msg.as_string())
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"SMTP error: {e}")
            return False
    
    def _send_with_local(self, to_emails: List[str], subject: str, content: str,
                        from_email: str = None, cc_emails: List[str] = None) -> bool:
        """Save email to local file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"email_{timestamp}.json"
            filepath = os.path.join(self.email_dir, filename)
            
            email_data = {
                'timestamp': datetime.now().isoformat(),
                'from': from_email or 'assistant@local.com',
                'to': to_emails,
                'cc': cc_emails or [],
                'subject': subject,
                'content': content
            }
            
            with open(filepath, 'w') as f:
                json.dump(email_data, f, indent=2)
            
            print(f"Email saved to: {filepath}")
            return True
            
        except Exception as e:
            print(f"Local email error: {e}")
            return False
    
    def _send_with_console(self, to_emails: List[str], subject: str, content: str,
                          from_email: str = None, cc_emails: List[str] = None) -> bool:
        """Print email to console"""
        try:
            print("\n" + "="*50)
            print("EMAIL SENT")
            print("="*50)
            print(f"From: {from_email or 'assistant@console.com'}")
            print(f"To: {', '.join(to_emails)}")
            if cc_emails:
                print(f"CC: {', '.join(cc_emails)}")
            print(f"Subject: {subject}")
            print("-"*50)
            print(content)
            print("="*50 + "\n")
            
            return True
            
        except Exception as e:
            print(f"Console email error: {e}")
            return False

    def _send_with_gmail(self, to_emails: List[str], subject: str, content: str, from_email: str = None, cc_emails: List[str] = None) -> bool:
        try:
            message = MIMEText(content)
            message['to'] = ', '.join(to_emails)
            message['from'] = from_email or "me"
            message['subject'] = subject
            if cc_emails:
                message['cc'] = ', '.join(cc_emails)
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            send_message = {'raw': raw_message}
            self.gmail_service.users().messages().send(userId="me", body=send_message).execute()
            return True
        except Exception as e:
            print(f"Gmail API error: {e}")
            return False
    
    def send_meeting_invite(self, meeting_details: Dict[str, Any], 
                           attendee_emails: List[str], organizer_email: str) -> bool:
        """
        Send meeting invitation email
        
        Args:
            meeting_details: Meeting details
            attendee_emails: List of attendee emails
            organizer_email: Organizer email
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Generate email content
            subject = f"Meeting: {meeting_details.get('title', 'Team Meeting')} - {meeting_details.get('date')} at {meeting_details.get('time')}"
            
            content = self._generate_meeting_invite_content(meeting_details, organizer_email)
            
            # Send email
            return self.send_email(
                to_emails=attendee_emails,
                subject=subject,
                content=content,
                from_email=organizer_email
            )
            
        except Exception as e:
            print(f"Error sending meeting invite: {e}")
            return False
    
    def send_dinner_invite(self, restaurant_details: Dict[str, Any],
                          attendee_emails: List[str], organizer_email: str) -> bool:
        """
        Send dinner invitation email
        
        Args:
            restaurant_details: Restaurant details
            attendee_emails: List of attendee emails
            organizer_email: Organizer email
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Generate email content
            subject = f"Team Dinner: {restaurant_details.get('name', 'Restaurant')} on {restaurant_details.get('date')}"
            
            content = self._generate_dinner_invite_content(restaurant_details, organizer_email)
            
            # Send email
            return self.send_email(
                to_emails=attendee_emails,
                subject=subject,
                content=content,
                from_email=organizer_email
            )
            
        except Exception as e:
            print(f"Error sending dinner invite: {e}")
            return False
    
    def _generate_meeting_invite_content(self, meeting_details: Dict[str, Any], organizer_email: str) -> str:
        """Generate meeting invitation email content"""
        
        if self.tone == "professional":
            content = f"""
Hi Team,

I've scheduled a meeting for {meeting_details.get('date')} at {meeting_details.get('time')}.

Meeting Details:
- Title: {meeting_details.get('title', 'Team Meeting')}
- Date: {meeting_details.get('date')}
- Time: {meeting_details.get('time')}
- Duration: {meeting_details.get('duration', '60')} minutes
- Location: {meeting_details.get('location', 'Conference Room')}
- Attendees: {', '.join(meeting_details.get('attendees', []))}

Please let me know if you need to reschedule.

Best regards,
{organizer_email}
            """.strip()
        
        elif self.tone == "casual":
            content = f"""
Hey everyone!

I've set up a meeting for {meeting_details.get('date')} at {meeting_details.get('time')}.

Here are the details:
- What: {meeting_details.get('title', 'Team Meeting')}
- When: {meeting_details.get('date')} at {meeting_details.get('time')}
- How long: {meeting_details.get('duration', '60')} minutes
- Where: {meeting_details.get('location', 'Conference Room')}
- Who: {', '.join(meeting_details.get('attendees', []))}

Let me know if this time doesn't work for you!

Cheers,
{organizer_email}
            """.strip()
        
        else:  # formal
            content = f"""
Dear Team Members,

This email serves as a formal invitation to attend a meeting scheduled for {meeting_details.get('date')} at {meeting_details.get('time')}.

Meeting Information:
- Meeting Title: {meeting_details.get('title', 'Team Meeting')}
- Date: {meeting_details.get('date')}
- Time: {meeting_details.get('time')}
- Duration: {meeting_details.get('duration', '60')} minutes
- Venue: {meeting_details.get('location', 'Conference Room')}
- Participants: {', '.join(meeting_details.get('attendees', []))}

Please confirm your attendance or notify us if you are unable to attend.

Sincerely,
{organizer_email}
            """.strip()
        
        return content
    
    def _generate_dinner_invite_content(self, restaurant_details: Dict[str, Any], organizer_email: str) -> str:
        """Generate dinner invitation email content"""
        
        if self.tone == "professional":
            content = f"""
Hi Team,

I've organized a team dinner for {restaurant_details.get('date')} at {restaurant_details.get('time')}.

Restaurant Details:
- Name: {restaurant_details.get('name', 'Restaurant')}
- Address: {restaurant_details.get('address', 'TBD')}
- Cuisine: {restaurant_details.get('cuisine', 'Various')}
- Rating: {restaurant_details.get('rating', 'N/A')}/5

Please confirm your attendance.

Best regards,
{organizer_email}
            """.strip()
        
        elif self.tone == "casual":
            content = f"""
Hey team!

I've booked a table for dinner on {restaurant_details.get('date')} at {restaurant_details.get('time')}.

Here's where we're going:
- Restaurant: {restaurant_details.get('name', 'Restaurant')}
- Address: {restaurant_details.get('address', 'TBD')}
- Food type: {restaurant_details.get('cuisine', 'Various')}
- Rating: {restaurant_details.get('rating', 'N/A')}/5

Let me know if you're in!

Cheers,
{organizer_email}
            """.strip()
        
        else:  # formal
            content = f"""
Dear Team Members,

You are cordially invited to attend a team dinner on {restaurant_details.get('date')} at {restaurant_details.get('time')}.

Venue Information:
- Establishment: {restaurant_details.get('name', 'Restaurant')}
- Address: {restaurant_details.get('address', 'TBD')}
- Cuisine: {restaurant_details.get('cuisine', 'Various')}
- Rating: {restaurant_details.get('rating', 'N/A')}/5

Please RSVP to confirm your attendance.

Sincerely,
{organizer_email}
            """.strip()
        
        return content
    
    def send_bulk_invites(self, recipients: List[str], template_type: str, 
                         details: Dict[str, Any], sender_email: str) -> Dict[str, Any]:
        """
        Send bulk invitations to multiple recipients
        
        Args:
            recipients: List of recipient emails
            template_type: Type of email template
            details: Email details
            sender_email: Sender email
        
        Returns:
            Dictionary with results
        """
        results = {
            'successful': [],
            'failed': [],
            'total': len(recipients)
        }
        
        for email in recipients:
            try:
                if template_type == "meeting_invite":
                    success = self.send_meeting_invite(details, [email], sender_email)
                elif template_type == "dinner_invite":
                    success = self.send_dinner_invite(details, [email], sender_email)
                else:
                    success = self.send_email([email], details.get('subject', ''), details.get('content', ''), sender_email)
                
                if success:
                    results['successful'].append(email)
                else:
                    results['failed'].append(email)
                    
            except Exception as e:
                print(f"Error sending to {email}: {e}")
                results['failed'].append(email)
        
        return results
    
    def get_sent_emails(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get list of sent emails (for local service)
        
        Args:
            limit: Maximum number of emails to return
        
        Returns:
            List of email data
        """
        if self.service != "local":
            return []
        
        try:
            emails = []
            files = os.listdir(self.email_dir)
            files.sort(reverse=True)  # Most recent first
            
            for filename in files[:limit]:
                if filename.endswith('.json'):
                    filepath = os.path.join(self.email_dir, filename)
                    with open(filepath, 'r') as f:
                        email_data = json.load(f)
                        emails.append(email_data)
            
            return emails
            
        except Exception as e:
            print(f"Error getting sent emails: {e}")
            return []
    
    def validate_email_address(self, email: str) -> bool:
        """
        Validate email address format
        
        Args:
            email: Email address to validate
        
        Returns:
            True if valid, False otherwise
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_email_list(self, emails: List[str]) -> Dict[str, List[str]]:
        """
        Validate a list of email addresses
        
        Args:
            emails: List of email addresses
        
        Returns:
            Dictionary with valid and invalid emails
        """
        valid_emails = []
        invalid_emails = []
        
        for email in emails:
            if self.validate_email_address(email):
                valid_emails.append(email)
            else:
                invalid_emails.append(email)
        
        return {
            'valid': valid_emails,
            'invalid': invalid_emails
        } 

    def send_event_notification(self, event_details: Dict[str, Any], action: str, sender_email: str) -> bool:
        """
        Send a notification email after a calendar event is created, deleted, or modified.
        Args:
            event_details: Event details dict
            action: 'created', 'deleted', or 'modified'
            sender_email: The email address of the sender/organizer
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            subject = f"[Calendar Event {action.title()}] {event_details.get('title', 'Event')} on {event_details.get('date', '')}"
            attendees = event_details.get('attendees', [])
            organizer = event_details.get('organizer', sender_email)
            to_emails = list(set(attendees + [organizer]))
            content = f"""
Hello,

This is to notify you that the following calendar event was {action}:

- Title: {event_details.get('title', 'Event')}
- Date: {event_details.get('date', '')}
- Time: {event_details.get('time', '')}
- Location: {event_details.get('location', '')}
- Organizer: {organizer}
- Attendees: {', '.join(attendees)}

If you have any questions, please contact the organizer.

Best regards,
Proactive Work-Life Assistant
"""
            return self.send_email(
                to_emails=to_emails,
                subject=subject,
                content=content,
                from_email=sender_email
            )
        except Exception as e:
            print(f"Error sending event notification: {e}")
            return False 