"""Email Fetcher component for retrieving and processing emails."""

import os
from typing import List, Dict
from .gmail_client import GmailClient

class EmailFetcher:
    """Component for fetching emails from Gmail and preparing them for processing."""
    
    def __init__(self, credentials_file: str = None, token_file: str = None):
        """Initialize Email Fetcher with Gmail client."""
        creds_file = credentials_file or os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
        token_file = token_file or os.getenv('GMAIL_TOKEN_FILE', 'token.json')
        
        self.gmail_client = GmailClient(creds_file, token_file)
        self.max_emails = int(os.getenv('MAX_EMAILS', 50))
    
    def fetch_recent_emails(self, query: str = "") -> List[Dict]:
        """Fetch recent emails from Gmail inbox."""
        print(f"Fetching up to {self.max_emails} recent emails...")
        
        emails = self.gmail_client.get_messages(
            max_results=self.max_emails,
            query=query
        )
        
        print(f"Retrieved {len(emails)} emails")
        return emails
    
    def fetch_unread_emails(self) -> List[Dict]:
        """Fetch only unread emails."""
        return self.fetch_recent_emails(query="is:unread")
    
    def fetch_emails_without_labels(self) -> List[Dict]:
        """Fetch emails that don't have custom labels (for categorization)."""
        # This will fetch emails that only have default Gmail labels
        return self.fetch_recent_emails(query="-label:Important -label:Newsletters -label:Promotions -label:Meetings -label:Personal")
    
    def get_email_summary(self, emails: List[Dict]) -> Dict:
        """Generate a summary of fetched emails."""
        if not emails:
            return {
                'total': 0,
                'unread': 0,
                'senders': [],
                'subjects': []
            }
        
        unread_count = 0
        senders = set()
        subjects = []
        
        for email in emails:
            if 'UNREAD' in email.get('labels', []):
                unread_count += 1
            
            sender = email.get('sender', '')
            if sender:
                # Extract email address from "Name <email@domain.com>" format
                if '<' in sender:
                    sender = sender.split('<')[1].split('>')[0]
                senders.add(sender)
            
            subject = email.get('subject', '')
            if subject:
                subjects.append(subject)
        
        return {
            'total': len(emails),
            'unread': unread_count,
            'senders': list(senders)[:10],  # Top 10 senders
            'subjects': subjects[:10]  # Top 10 subjects
        }
    
    def filter_emails_by_sender(self, emails: List[Dict], sender_domain: str) -> List[Dict]:
        """Filter emails by sender domain."""
        filtered = []
        for email in emails:
            sender = email.get('sender', '')
            if sender_domain.lower() in sender.lower():
                filtered.append(email)
        return filtered
    
    def filter_emails_by_keyword(self, emails: List[Dict], keyword: str) -> List[Dict]:
        """Filter emails containing specific keywords in subject or body."""
        filtered = []
        keyword_lower = keyword.lower()
        
        for email in emails:
            subject = email.get('subject', '').lower()
            body = email.get('body', '').lower()
            snippet = email.get('snippet', '').lower()
            
            if (keyword_lower in subject or 
                keyword_lower in body or 
                keyword_lower in snippet):
                filtered.append(email)
        
        return filtered
    
    def prepare_email_for_processing(self, email: Dict) -> Dict:
        """Prepare email data for agent processing."""
        return {
            'id': email.get('id'),
            'subject': email.get('subject', ''),
            'sender': email.get('sender', ''),
            'recipient': email.get('recipient', ''),
            'date': email.get('date', ''),
            'body': email.get('body', ''),
            'snippet': email.get('snippet', ''),
            'labels': email.get('labels', []),
            'thread_id': email.get('thread_id', ''),
            'is_unread': 'UNREAD' in email.get('labels', [])
        }