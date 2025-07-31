"""Local AI Agents using Ollama with llama3.2:3b."""

import os
import json
import requests
from typing import Dict, List, Optional

class OllamaEmailCategorizerAgent:
    """Agent for categorizing emails using local Ollama llama3.2:3b model."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """Initialize the categorizer agent with Ollama."""
        self.ollama_url = ollama_url
        self.model = "llama3.2:3b"
        self.categories = os.getenv('EMAIL_CATEGORIES', 'Important,Newsletters,Promotions,Meetings,Personal').split(',')
        
        # Test Ollama connection
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code != 200:
                raise ConnectionError("Ollama not running")
        except Exception as e:
            print(f"⚠️  Warning: Cannot connect to Ollama at {ollama_url}. Please start Ollama with: ollama serve")
            print(f"   Error: {e}")
    
    def _call_ollama(self, prompt: str, max_tokens: int = 50) -> str:
        """Make API call to local Ollama instance."""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                print(f"Ollama API error: {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return ""
    
    def categorize_email(self, email_data: Dict) -> str:
        """Categorize a single email using Ollama."""
        try:
            # Truncate content to avoid long prompts
            subject = email_data.get('subject', '')[:100]
            sender = email_data.get('sender', '')[:50]  
            snippet = email_data.get('snippet', '')[:200]
            
            prompt = f"""Categorize this email into exactly one category: {', '.join(self.categories)}

Category definitions:
- Important: Urgent business matters, security alerts, deadlines, work tasks, university communications
- Newsletters: Weekly/monthly updates, tech news, subscriptions, digest emails
- Promotions: Sales offers, discounts, marketing emails, advertisements, job alerts
- Meetings: Meeting requests, calendar invites, scheduling discussions, availability inquiries
- Personal: Personal communications, family, friends, social media notifications

Email to categorize:
Subject: {subject}
Sender: {sender}
Content: {snippet}

Respond with ONLY the category name from the list above."""

            response = self._call_ollama(prompt, max_tokens=20)
            
            # Clean and validate response
            raw_response = response.strip()
            category = raw_response.title()
            
            # Handle common variations
            if 'newsletter' in category.lower() or 'news' in category.lower():
                category = 'Newsletters'
            elif 'promotion' in category.lower() or 'promo' in category.lower():
                category = 'Promotions'
            elif 'meeting' in category.lower() or 'schedule' in category.lower():
                category = 'Meetings'
            elif 'important' in category.lower() or 'urgent' in category.lower():
                category = 'Important'
            elif 'personal' in category.lower():
                category = 'Personal'
            
            if category in self.categories:
                return category
            else:
                # Fallback logic based on content
                all_text = f"{subject} {sender} {snippet}".lower()
                
                if any(word in all_text for word in ['offer', 'discount', 'sale', '%', 'buy', 'shop']):
                    return 'Promotions'
                elif any(word in all_text for word in ['newsletter', 'digest', 'weekly', 'update']):
                    return 'Newsletters'
                elif any(word in all_text for word in ['meeting', 'schedule', 'calendar', 'availability']):
                    return 'Meetings'
                elif any(word in all_text for word in ['urgent', 'important', 'action required', 'verify']):
                    return 'Important'
                elif any(word in all_text for word in ['birthday', 'family', 'personal']):
                    return 'Personal'
                else:
                    return 'Important'  # Default fallback
                
        except Exception as e:
            print(f"Error categorizing email with Ollama: {e}")
            return 'Important'  # Default fallback
    
    def categorize_batch(self, emails: List[Dict]) -> List[Dict]:
        """Categorize multiple emails."""
        categorized = []
        
        print(f"🦙 Using Ollama llama3.2:3b for local categorization (FREE)")
        
        for i, email in enumerate(emails, 1):
            category = self.categorize_email(email)
            email_with_category = email.copy()
            email_with_category['ai_category'] = category
            categorized.append(email_with_category)
            
            # Progress indicator
            if i % 10 == 0:
                print(f"   Processed {i}/{len(emails)} emails...")
        
        return categorized


class OllamaEmailResponderAgent:
    """Agent for generating email responses using Ollama."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """Initialize the responder agent with Ollama."""
        self.ollama_url = ollama_url
        self.model = "llama3.2:3b"
    
    def _call_ollama(self, prompt: str, max_tokens: int = 300) -> str:
        """Make API call to local Ollama instance."""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                return ""
                
        except Exception as e:
            print(f"Error calling Ollama for response: {e}")
            return ""
    
    def should_respond(self, email_data: Dict) -> bool:
        """Use rule-based logic to determine if email needs response (fast and free)."""
        subject = email_data.get('subject', '').lower()
        sender = email_data.get('sender', '').lower()
        snippet = email_data.get('snippet', '').lower()
        
        # Don't respond to these patterns
        no_respond_patterns = [
            'newsletter', 'digest', 'unsubscribe', 'notification',
            'noreply', 'no-reply', 'donotreply', 'automated',
            'system', 'bot', 'updates-noreply', 'notifications@'
        ]
        
        all_text = f"{subject} {sender} {snippet}"
        
        # Check no-respond patterns first
        for pattern in no_respond_patterns:
            if pattern in all_text:
                return False
        
        # Respond to these patterns
        respond_patterns = [
            'question', '?', 'inquiry', 'request', 'help', 'need',
            'meeting', 'schedule', 'availability', 'urgent',
            'important', 'please', 'can you', 'would you', 'could you'
        ]
        
        for pattern in respond_patterns:
            if pattern in all_text:
                return True
        
        return False
    
    def generate_response(self, email_data: Dict, context: str = "") -> str:
        """Generate a response using Ollama."""
        try:
            # Truncate content
            subject = email_data.get('subject', '')[:100]
            sender = email_data.get('sender', '')[:50]
            body = (email_data.get('body', '') or email_data.get('snippet', ''))[:300]
            
            prompt = f"""Generate a professional email response to this email.

Guidelines:
- Keep it concise and professional
- Address the key points
- Don't make commitments
- Include appropriate greeting and closing

Original Email:
Subject: {subject}
From: {sender}
Content: {body}

Generate a professional response (email body only, no subject line):"""

            response = self._call_ollama(prompt, max_tokens=400)
            
            if response:
                return response
            else:
                return "Thank you for your email. I'll review this and get back to you soon."
                
        except Exception as e:
            print(f"Error generating response with Ollama: {e}")
            return "Thank you for your email. I'll review this and get back to you soon."


class OllamaMeetingSchedulerAgent:
    """Agent for detecting meeting requests using Ollama."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """Initialize the scheduler agent with Ollama."""
        self.ollama_url = ollama_url
        self.model = "llama3.2:3b"
    
    def is_meeting_request(self, email_data: Dict) -> bool:
        """Use rule-based logic for meeting detection (fast and accurate)."""
        subject = email_data.get('subject', '').lower()
        snippet = email_data.get('snippet', '').lower()
        
        meeting_keywords = [
            'meeting', 'schedule', 'calendar', 'appointment', 'call',
            'conference', 'zoom', 'teams', 'meet', 'session', 'webinar',
            'availability', 'available', 'free time', 'book time',
            'let\'s talk', 'discuss', 'catch up', 'invite'
        ]
        
        all_text = f"{subject} {snippet}"
        
        for keyword in meeting_keywords:
            if keyword in all_text:
                return True
        
        return False
    
    def _call_ollama(self, prompt: str, max_tokens: int = 200) -> str:
        """Make API call to local Ollama instance."""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                return ""
                
        except Exception as e:
            print(f"Error calling Ollama for meeting details: {e}")
            return ""
    
    def extract_meeting_details(self, email_data: Dict) -> Dict:
        """Extract meeting details using Ollama."""
        try:
            subject = email_data.get('subject', '')[:100]
            body = (email_data.get('body', '') or email_data.get('snippet', ''))[:300]
            
            prompt = f"""Extract meeting details from this email as JSON:

Email:
Subject: {subject}
Content: {body}

Extract these details in JSON format:
{{"meeting_type": "call/video/in-person", "duration": minutes_number, "purpose": "brief_description", "urgency": "high/medium/low"}}

Return only the JSON, no other text:"""

            response = self._call_ollama(prompt, max_tokens=150)
            
            if response:
                try:
                    # Clean up the response to extract JSON
                    if '```json' in response:
                        response = response.split('```json')[1].split('```')[0]
                    elif '```' in response:
                        response = response.split('```')[1].split('```')[0]
                    
                    details = json.loads(response.strip())
                    return details
                except json.JSONDecodeError:
                    pass
            
            # Fallback with rule-based detection
            all_text = f"{subject} {body}".lower()
            
            # Determine meeting type
            if any(word in all_text for word in ['zoom', 'teams', 'video', 'online']):
                meeting_type = 'video'
            elif any(word in all_text for word in ['call', 'phone']):
                meeting_type = 'call'
            elif any(word in all_text for word in ['office', 'in-person', 'location']):
                meeting_type = 'in-person'
            else:
                meeting_type = 'call'
            
            # Determine urgency
            if any(word in all_text for word in ['urgent', 'asap', 'immediately', 'today']):
                urgency = 'high'
            elif any(word in all_text for word in ['soon', 'this week', 'quickly']):
                urgency = 'medium'
            else:
                urgency = 'low'
            
            return {
                'meeting_type': meeting_type,
                'duration': 60,
                'purpose': f"Discussion about {subject}",
                'urgency': urgency
            }
            
        except Exception as e:
            print(f"Error extracting meeting details: {e}")
            return {
                'meeting_type': 'call',
                'duration': 60,
                'purpose': 'Meeting discussion',
                'urgency': 'medium'
            }
    
    def generate_scheduling_response(self, email_data: Dict, suggested_times: List[Dict]) -> str:
        """Generate a response with suggested meeting times using Ollama."""
        try:
            times_text = "\n".join([
                f"- {time['formatted_start']} to {time['formatted_end']}"
                for time in suggested_times[:3]
            ])
            
            subject = email_data.get('subject', '')[:100]
            sender = email_data.get('sender', '')[:50]
            
            prompt = f"""Generate a professional email response for a meeting request with suggested times.

Original request:
Subject: {subject}
From: {sender}

Available times:
{times_text}

Write a professional response that:
- Acknowledges the meeting request
- Provides the suggested times
- Asks for confirmation
- Includes a professional closing

Response:"""

            response = self._call_ollama(prompt, max_tokens=300)
            
            if response:
                return response
            else:
                return f"Thank you for the meeting request. I have availability at the following times:\n\n{times_text}\n\nPlease let me know which time works best for you."
                
        except Exception as e:
            print(f"Error generating scheduling response: {e}")
            return f"Thank you for the meeting request. I have some availability and will get back to you with specific times soon."