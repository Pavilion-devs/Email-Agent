"""Gmail API Client for fetching and sending emails."""

import os
import json
import base64
from datetime import datetime
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GmailClient:
    """Gmail API client for email operations."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.labels',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.json"):
        """Initialize Gmail client with OAuth credentials."""
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2."""
        creds = None
        
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file {self.credentials_file} not found. "
                        "Please download it from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
    
    def get_messages(self, max_results: int = 50, query: str = "") -> List[Dict]:
        """Fetch email messages from Gmail inbox."""
        try:
            results = self.service.users().messages().list(
                userId='me', 
                maxResults=max_results,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            detailed_messages = []
            
            for message in messages:
                msg_detail = self.service.users().messages().get(
                    userId='me', 
                    id=message['id'],
                    format='full'
                ).execute()
                
                email_data = self._parse_message(msg_detail)
                detailed_messages.append(email_data)
            
            return detailed_messages
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def _parse_message(self, message: Dict) -> Dict:
        """Parse Gmail message into structured format."""
        headers = message['payload'].get('headers', [])
        
        email_data = {
            'id': message['id'],
            'thread_id': message['threadId'],
            'labels': message.get('labelIds', []),
            'timestamp': int(message['internalDate']) / 1000,
            'date': datetime.fromtimestamp(int(message['internalDate']) / 1000).isoformat(),
            'subject': '',
            'sender': '',
            'recipient': '',
            'body': '',
            'snippet': message.get('snippet', '')
        }
        
        for header in headers:
            name = header['name'].lower()
            if name == 'subject':
                email_data['subject'] = header['value']
            elif name == 'from':
                email_data['sender'] = header['value']
            elif name == 'to':
                email_data['recipient'] = header['value']
        
        email_data['body'] = self._extract_body(message['payload'])
        return email_data
    
    def _extract_body(self, payload: Dict) -> str:
        """Extract email body from message payload."""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
                elif part['mimeType'] == 'text/html':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
        elif payload['body'].get('data'):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body
    
    def send_email(self, to: str, subject: str, body: str, reply_to_id: str = None) -> bool:
        """Send an email reply."""
        try:
            message = self._create_message(to, subject, body, reply_to_id)
            
            result = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            print(f"Email sent successfully. Message ID: {result['id']}")
            return True
            
        except HttpError as error:
            print(f'An error occurred while sending email: {error}')
            return False
    
    def _create_message(self, to: str, subject: str, body: str, reply_to_id: str = None) -> Dict:
        """Create email message in Gmail API format."""
        import email.mime.text
        import email.mime.multipart
        
        msg = email.mime.multipart.MIMEMultipart()
        msg['to'] = to
        msg['subject'] = subject
        
        if reply_to_id:
            msg['In-Reply-To'] = reply_to_id
            msg['References'] = reply_to_id
        
        msg.attach(email.mime.text.MIMEText(body, 'plain'))
        
        raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
        return {'raw': raw_message}
    
    def add_label(self, message_id: str, label_name: str) -> bool:
        """Add a label to an email message."""
        try:
            labels = self.service.users().labels().list(userId='me').execute()
            label_id = None
            
            for label in labels.get('labels', []):
                if label['name'] == label_name:
                    label_id = label['id']
                    break
            
            if not label_id:
                label_id = self._create_label(label_name)
            
            if label_id:
                self.service.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body={'addLabelIds': [label_id]}
                ).execute()
                return True
            
        except HttpError as error:
            print(f'An error occurred while adding label: {error}')
        
        return False
    
    def _create_label(self, label_name: str) -> Optional[str]:
        """Create a new Gmail label."""
        try:
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            
            result = self.service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()
            
            return result['id']
            
        except HttpError as error:
            print(f'An error occurred while creating label: {error}')
            return None