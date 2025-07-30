"""Simplified AI Agents using direct OpenAI API calls."""

import os
import json
from typing import Dict, List, Optional
from openai import OpenAI

class EmailCategorizerAgent:
    """Agent for categorizing emails into predefined categories."""
    
    def __init__(self, api_key: str = None):
        """Initialize the categorizer agent."""
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=api_key)
        self.categories = os.getenv('EMAIL_CATEGORIES', 'Important,Newsletters,Promotions,Meetings,Personal').split(',')
    
    def categorize_email(self, email_data: Dict) -> str:
        """Categorize a single email."""
        try:
            prompt = f"""Categorize this email into exactly one of these categories: {', '.join(self.categories)}

Category definitions:
- Important: Urgent business matters, project updates, client communications, deadlines, work-related tasks
- Newsletters: Weekly/monthly updates, tech industry news, subscriptions, regular informational emails
- Promotions: Sales offers, discounts, marketing emails, advertisements, limited time offers
- Meetings: Meeting requests, calendar invites, scheduling discussions, availability inquiries
- Personal: Personal communications, family, friends, birthday wishes, non-work related

Email to categorize:
Subject: {email_data.get('subject', '')}
Sender: {email_data.get('sender', '')}
Content: {email_data.get('snippet', '')}

Respond with ONLY the category name."""

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=50
            )
            
            category = response.choices[0].message.content.strip()
            if category in self.categories:
                return category
            else:
                return 'Important'  # Default fallback
                
        except Exception as e:
            print(f"Error categorizing email: {e}")
            return 'Important'  # Default fallback
    
    def categorize_batch(self, emails: List[Dict]) -> List[Dict]:
        """Categorize multiple emails."""
        categorized = []
        
        for email in emails:
            category = self.categorize_email(email)
            email_with_category = email.copy()
            email_with_category['ai_category'] = category
            categorized.append(email_with_category)
        
        return categorized


class EmailResponderAgent:
    """Agent for generating email responses."""
    
    def __init__(self, api_key: str = None):
        """Initialize the responder agent."""
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=api_key)
    
    def should_respond(self, email_data: Dict) -> bool:
        """Determine if an email should receive an auto-response."""
        try:
            prompt = f"""Determine if this email should receive an automated response.

Respond with 'YES' for:
- Questions that need answers
- Meeting requests
- Project inquiries
- Client communications requiring acknowledgment

Respond with 'NO' for:
- Newsletters
- Promotional emails
- Automated notifications
- Spam or low-priority items

Email:
Subject: {email_data.get('subject', '')}
Sender: {email_data.get('sender', '')}
Content: {email_data.get('snippet', '')}

Respond with only 'YES' or 'NO'."""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip().upper()
            return result == 'YES'
            
        except Exception as e:
            print(f"Error determining response need: {e}")
            return False
    
    def generate_response(self, email_data: Dict, context: str = "") -> str:
        """Generate a response to an email."""
        try:
            prompt = f"""Generate a professional email response to this email.

Guidelines:
- Keep responses concise and professional
- Match the tone of the original email
- Address the key points raised
- Include appropriate greeting and closing
- Do not make commitments without explicit instruction

Original Email:
Subject: {email_data.get('subject', '')}
From: {email_data.get('sender', '')}
Content: {email_data.get('body', '') or email_data.get('snippet', '')}

Generate an appropriate response (email body only, no subject)."""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Thank you for your email. I'll review this and get back to you soon."


class MeetingSchedulerAgent:
    """Agent for detecting meeting requests and suggesting times."""
    
    def __init__(self, api_key: str = None):
        """Initialize the scheduler agent."""
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=api_key)
    
    def is_meeting_request(self, email_data: Dict) -> bool:
        """Check if email contains a meeting request."""
        try:
            prompt = f"""Analyze this email to determine if it contains a meeting request or scheduling discussion.

Look for:
- Direct meeting requests ("let's schedule", "can we meet")
- Availability inquiries ("when are you free", "available times")
- Calendar invitations or scheduling language
- Discussion of meetings, calls, or appointments

Email:
Subject: {email_data.get('subject', '')}
Sender: {email_data.get('sender', '')}
Content: {email_data.get('body', '') or email_data.get('snippet', '')}

Respond with 'YES' if the email is about scheduling/meetings, 'NO' otherwise."""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip().upper()
            return result == 'YES'
            
        except Exception as e:
            print(f"Error detecting meeting request: {e}")
            return False
    
    def extract_meeting_details(self, email_data: Dict) -> Dict:
        """Extract meeting details from email."""
        try:
            prompt = f"""Extract meeting details from this email and format as JSON.

Extract:
- meeting_type: type of meeting (call, in-person, video, etc.)
- duration: estimated duration in minutes (default 60)
- purpose: brief description of meeting purpose
- urgency: high/medium/low based on language used
- participants: list of mentioned participants (emails if available)

Email:
Subject: {email_data.get('subject', '')}
Sender: {email_data.get('sender', '')}
Content: {email_data.get('body', '') or email_data.get('snippet', '')}

Format as JSON only, no other text."""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300
            )
            
            result = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            details = json.loads(result)
            return details
            
        except Exception as e:
            print(f"Error extracting meeting details: {e}")
            return {
                'meeting_type': 'call',
                'duration': 60,
                'purpose': 'Meeting discussion',
                'urgency': 'medium',
                'participants': []
            }
    
    def generate_scheduling_response(self, email_data: Dict, suggested_times: List[Dict]) -> str:
        """Generate a response with suggested meeting times."""
        try:
            times_text = "\n".join([
                f"- {time['formatted_start']} to {time['formatted_end']}"
                for time in suggested_times[:3]
            ])
            
            prompt = f"""Generate a professional email response for a meeting request with suggested times.

Include:
- Acknowledgment of the meeting request
- Suggested available times
- Request for confirmation
- Professional closing

Original meeting request:
Subject: {email_data.get('subject', '')}
From: {email_data.get('sender', '')}

Suggested available times:
{times_text}

Generate an appropriate response."""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating scheduling response: {e}")
            return f"Thank you for the meeting request. I have some availability and will get back to you with specific times soon."