"""Google Calendar API Client for meeting scheduling."""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class CalendarClient:
    """Google Calendar API client for scheduling operations."""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, credentials_file: str = "calendar_credentials.json", token_file: str = "calendar_token.json"):
        """Initialize Calendar client with OAuth credentials."""
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API using OAuth2."""
        creds = None
        
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Calendar credentials file {self.credentials_file} not found. "
                        "Please download it from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    def get_free_busy(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Check free/busy status for a time range."""
        try:
            body = {
                "timeMin": start_time.isoformat() + 'Z',
                "timeMax": end_time.isoformat() + 'Z',
                "items": [{"id": "primary"}]
            }
            
            result = self.service.freebusy().query(body=body).execute()
            busy_times = result.get('calendars', {}).get('primary', {}).get('busy', [])
            
            return busy_times
            
        except HttpError as error:
            print(f'An error occurred checking free/busy: {error}')
            return []
    
    def suggest_meeting_times(self, duration_minutes: int = 60, days_ahead: int = 7) -> List[Dict]:
        """Suggest available meeting times."""
        suggestions = []
        start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        for day in range(days_ahead):
            current_date = start_date + timedelta(days=day)
            
            if current_date.weekday() >= 5:  # Skip weekends
                continue
            
            for hour in range(9, 17):  # 9 AM to 5 PM
                meeting_start = current_date.replace(hour=hour)
                meeting_end = meeting_start + timedelta(minutes=duration_minutes)
                
                busy_times = self.get_free_busy(meeting_start, meeting_end)
                
                if not busy_times:  # Time slot is free
                    suggestions.append({
                        'start': meeting_start.isoformat(),
                        'end': meeting_end.isoformat(),
                        'formatted_start': meeting_start.strftime('%A, %B %d at %I:%M %p'),
                        'formatted_end': meeting_end.strftime('%I:%M %p')
                    })
                
                if len(suggestions) >= 3:  # Limit to 3 suggestions
                    break
            
            if len(suggestions) >= 3:
                break
        
        return suggestions
    
    def create_event(self, title: str, start_time: datetime, end_time: datetime, 
                    attendees: List[str] = None, description: str = "") -> Optional[str]:
        """Create a calendar event."""
        try:
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/New_York',  # Adjust timezone as needed
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/New_York',
                },
            }
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            result = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            print(f"Event created: {result.get('htmlLink')}")
            return result.get('id')
            
        except HttpError as error:
            print(f'An error occurred creating event: {error}')
            return None
    
    def create_meeting_from_email(self, email_data: Dict, suggested_times: List[Dict]) -> Optional[str]:
        """Create a meeting based on email content and suggested times."""
        if not suggested_times:
            return None
        
        # Use the first suggested time
        first_suggestion = suggested_times[0]
        start_time = datetime.fromisoformat(first_suggestion['start'])
        end_time = datetime.fromisoformat(first_suggestion['end'])
        
        # Extract attendee email from sender
        sender_email = email_data.get('sender', '')
        if '<' in sender_email:
            sender_email = sender_email.split('<')[1].split('>')[0]
        
        title = f"Meeting: {email_data.get('subject', 'Scheduled Meeting')}"
        description = f"Meeting scheduled based on email request.\n\nOriginal email:\n{email_data.get('snippet', '')}"
        
        return self.create_event(
            title=title,
            start_time=start_time,
            end_time=end_time,
            attendees=[sender_email] if sender_email else None,
            description=description
        )