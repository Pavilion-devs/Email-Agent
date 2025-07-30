"""Hybrid AI Agents using rule-based filtering + Gemini 1.5 Flash backup."""

import os
import re
import time
import json
from typing import Dict, List, Optional
import google.generativeai as genai
from openai import OpenAI

class HybridEmailCategorizerAgent:
    """Hybrid agent using rule-based filtering + Gemini 1.5 Flash backup."""
    
    def __init__(self, google_api_key: str = None, openai_api_key: str = None):
        """Initialize the hybrid categorizer agent."""
        # Set up Gemini
        google_api_key = google_api_key or os.getenv('GOOGLE_API_KEY')
        if google_api_key:
            genai.configure(api_key=google_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.gemini_model = None
        
        # Set up OpenAI as fallback
        openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
        else:
            self.openai_client = None
        
        self.categories = os.getenv('EMAIL_CATEGORIES', 'Important,Newsletters,Promotions,Meetings,Personal').split(',')
        
        # Rule patterns for fast categorization
        self.promotion_patterns = [
            r'\b(offer|discount|sale|promo|deal|save|free|limited\s+time|special\s+price|%\s*off)\b',
            r'\b(buy\s+now|shop\s+now|order\s+now|get\s+yours|upgrade\s+now)\b',
            r'\b(black\s+friday|cyber\s+monday|flash\s+sale|clearance)\b'
        ]
        
        self.newsletter_patterns = [
            r'\b(newsletter|digest|weekly|monthly|daily|update|roundup)\b',
            r'\b(unsubscribe|manage\s+preferences|view\s+in\s+browser)\b',
            r'@(newsletter|digest|updates|news|mail|email)\.',
            r'\b(tech\s+news|industry\s+news|latest\s+news)\b'
        ]
        
        self.meeting_patterns = [
            r'\b(meeting|schedule|calendar|appointment|call|conference)\b',
            r'\b(available|availability|free\s+time|book\s+time)\b',
            r'\b(zoom|teams|google\s+meet|webinar|session)\b',
            r'\b(let\'?s\s+(meet|talk|discuss|schedule))\b'
        ]
        
        self.important_patterns = [
            r'\b(urgent|important|action\s+required|deadline|expires?)\b',
            r'\b(verify|verification|confirm|security|alert)\b',
            r'\b(payment|invoice|bill|account|suspended)\b',
            r'\b(login|password|access|unauthorized)\b'
        ]
        
        self.personal_patterns = [
            r'\b(happy\s+birthday|congratulations|family|mom|dad)\b',
            r'@(gmail\.com|yahoo\.com|hotmail\.com|icloud\.com)$',
            r'\b(love|miss|see\s+you|can\'?t\s+wait)\b'
        ]
    
    def rule_based_categorize(self, email_data: Dict) -> str:
        """Fast rule-based categorization."""
        subject = email_data.get('subject', '').lower()
        sender = email_data.get('sender', '').lower()
        snippet = email_data.get('snippet', '').lower()
        
        # Combine all text for pattern matching
        all_text = f"{subject} {sender} {snippet}"
        
        # Count pattern matches for each category
        scores = {
            'Promotions': self._count_patterns(all_text, self.promotion_patterns),
            'Newsletters': self._count_patterns(all_text, self.newsletter_patterns),
            'Meetings': self._count_patterns(all_text, self.meeting_patterns),
            'Important': self._count_patterns(all_text, self.important_patterns),
            'Personal': self._count_patterns(all_text, self.personal_patterns)
        }
        
        # Additional heuristics
        # Newsletter indicators
        if any(keyword in sender for keyword in ['newsletter', 'digest', 'noreply', 'no-reply', 'updates']):
            scores['Newsletters'] += 2
        
        # Promotion indicators
        if any(keyword in subject for keyword in ['%', 'off', 'free', 'sale', 'offer']):
            scores['Promotions'] += 2
        
        # Meeting indicators
        if any(keyword in subject for keyword in ['meeting', 'schedule', 'calendar', 'invite']):
            scores['Meetings'] += 2
        
        # Important indicators
        if any(keyword in subject for keyword in ['urgent', 'action required', 'verify', 'security']):
            scores['Important'] += 2
        
        # Find the category with highest score
        max_score = max(scores.values())
        
        # If no clear winner (score < 2), return "uncertain"
        if max_score < 2:
            return "uncertain"
        
        # Return category with highest score
        for category, score in scores.items():
            if score == max_score:
                return category
        
        return "uncertain"
    
    def _count_patterns(self, text: str, patterns: List[str]) -> int:
        """Count how many patterns match in the text."""
        count = 0
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                count += 1
        return count
    
    def gemini_categorize(self, email_data: Dict) -> str:
        """Use Gemini 1.5 Flash for uncertain cases."""
        if not self.gemini_model:
            return "Important"  # Fallback
        
        try:
            # Truncate content to avoid token limits
            subject = email_data.get('subject', '')[:100]
            sender = email_data.get('sender', '')[:100]
            snippet = email_data.get('snippet', '')[:200]
            
            prompt = f"""Categorize this email into exactly one category: {', '.join(self.categories)}

Categories:
- Important: Urgent business matters, security alerts, deadlines, work tasks
- Newsletters: Regular updates, tech news, subscriptions, digests
- Promotions: Sales, discounts, marketing, job alerts, advertisements  
- Meetings: Meeting requests, calendar invites, scheduling discussions
- Personal: Personal communications, family, friends, social media

Email:
Subject: {subject}
Sender: {sender}
Content: {snippet}

Respond with ONLY the category name."""

            response = self.gemini_model.generate_content(prompt)
            category = response.text.strip()
            
            if category in self.categories:
                return category
            else:
                return 'Important'  # Default fallback
                
        except Exception as e:
            print(f"Gemini categorization failed: {e}")
            return self.openai_fallback(email_data)
    
    def openai_fallback(self, email_data: Dict) -> str:
        """OpenAI fallback for when Gemini fails."""
        if not self.openai_client:
            return "Important"
        
        try:
            # Truncate content
            subject = email_data.get('subject', '')[:100]
            sender = email_data.get('sender', '')[:100]
            snippet = email_data.get('snippet', '')[:200]
            
            prompt = f"""Categorize this email into one category: {', '.join(self.categories)}

Email: Subject: {subject}, Sender: {sender}, Content: {snippet}

Respond with ONLY the category name."""

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=20
            )
            
            category = response.choices[0].message.content.strip()
            return category if category in self.categories else 'Important'
            
        except Exception as e:
            print(f"OpenAI fallback failed: {e}")
            return 'Important'
    
    def categorize_email(self, email_data: Dict) -> Dict:
        """Main categorization method with cost tracking."""
        start_time = time.time()
        
        # Step 1: Try rule-based categorization (free)
        rule_category = self.rule_based_categorize(email_data)
        
        if rule_category != "uncertain":
            return {
                'category': rule_category,
                'method': 'rule-based',
                'cost': 0,
                'processing_time': time.time() - start_time,
                'confidence': 'high'
            }
        
        # Step 2: Use Gemini 1.5 Flash for uncertain cases (cheap)
        ai_category = self.gemini_categorize(email_data)
        
        return {
            'category': ai_category,
            'method': 'gemini-flash',
            'cost': 0.0001,  # Approximate cost
            'processing_time': time.time() - start_time,
            'confidence': 'medium'
        }
    
    def categorize_batch(self, emails: List[Dict]) -> List[Dict]:
        """Categorize multiple emails with cost tracking."""
        results = []
        total_cost = 0
        rule_based_count = 0
        ai_count = 0
        
        for email in emails:
            result = self.categorize_email(email)
            
            # Add category to email data
            email_with_category = email.copy()
            email_with_category['ai_category'] = result['category']
            email_with_category['categorization_method'] = result['method']
            email_with_category['processing_cost'] = result['cost']
            
            results.append(email_with_category)
            
            # Track statistics
            total_cost += result['cost']
            if result['method'] == 'rule-based':
                rule_based_count += 1
            else:
                ai_count += 1
        
        print(f"\n💰 Categorization Cost Summary:")
        print(f"   Rule-based (free): {rule_based_count} emails")
        print(f"   AI-powered: {ai_count} emails")
        print(f"   Total cost: ${total_cost:.4f}")
        print(f"   Average cost per email: ${total_cost/len(emails):.4f}")
        
        return results


class CostOptimizedResponderAgent:
    """Response agent with cost optimization."""
    
    def __init__(self, google_api_key: str = None, openai_api_key: str = None):
        """Initialize the cost-optimized responder agent."""
        google_api_key = google_api_key or os.getenv('GOOGLE_API_KEY')
        if google_api_key:
            genai.configure(api_key=google_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.gemini_model = None
        
        openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
        else:
            self.openai_client = None
    
    def should_respond(self, email_data: Dict) -> bool:
        """Quick rule-based check if email needs response."""
        subject = email_data.get('subject', '').lower()
        sender = email_data.get('sender', '').lower()
        snippet = email_data.get('snippet', '').lower()
        
        # Auto-respond patterns
        respond_patterns = [
            r'\b(question|\?|inquiry|request|help|need|require)\b',
            r'\b(meeting|schedule|availability|when|time)\b',
            r'\b(please|can\s+you|would\s+you|could\s+you)\b',
            r'\b(urgent|important|asap|immediately)\b'
        ]
        
        # Don't respond patterns
        no_respond_patterns = [
            r'\b(newsletter|digest|unsubscribe|notification)\b',
            r'\b(noreply|no-reply|donotreply|do-not-reply)\b',
            r'\b(automated|automatic|system|bot)\b',
            r'@(newsletter|digest|noreply|notification)\.'
        ]
        
        all_text = f"{subject} {sender} {snippet}"
        
        # Check no-respond patterns first
        for pattern in no_respond_patterns:
            if re.search(pattern, all_text, re.IGNORECASE):
                return False
        
        # Check respond patterns
        for pattern in respond_patterns:
            if re.search(pattern, all_text, re.IGNORECASE):
                return True
        
        return False
    
    def generate_response(self, email_data: Dict) -> str:
        """Generate response using Gemini first, OpenAI as fallback."""
        if self.gemini_model:
            try:
                # Truncate content
                subject = email_data.get('subject', '')[:100]
                sender = email_data.get('sender', '')[:100]
                body = (email_data.get('body', '') or email_data.get('snippet', ''))[:500]
                
                prompt = f"""Generate a professional email response.

Guidelines:
- Keep it concise and professional
- Address key points
- Don't make commitments
- Include appropriate greeting and closing

Original Email:
Subject: {subject}
From: {sender}
Content: {body}

Generate response (email body only)."""

                response = self.gemini_model.generate_content(prompt)
                return response.text.strip()
                
            except Exception as e:
                print(f"Gemini response generation failed: {e}")
        
        # OpenAI fallback  
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=300
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"OpenAI response generation failed: {e}")
        
        return "Thank you for your email. I'll review this and get back to you soon."


class CostOptimizedMeetingAgent:
    """Meeting detection agent with cost optimization."""
    
    def __init__(self, google_api_key: str = None):
        """Initialize the meeting agent."""
        google_api_key = google_api_key or os.getenv('GOOGLE_API_KEY')
        if google_api_key:
            genai.configure(api_key=google_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.gemini_model = None
    
    def is_meeting_request(self, email_data: Dict) -> bool:
        """Rule-based meeting detection (free)."""
        subject = email_data.get('subject', '').lower()
        snippet = email_data.get('snippet', '').lower()
        
        meeting_keywords = [
            'meeting', 'schedule', 'calendar', 'appointment', 'call',
            'conference', 'zoom', 'teams', 'meet', 'session', 'webinar',
            'availability', 'available', 'free time', 'book time',
            'let\'s talk', 'discuss', 'catch up'
        ]
        
        all_text = f"{subject} {snippet}"
        
        for keyword in meeting_keywords:
            if keyword in all_text:
                return True
        
        return False
    
    def extract_meeting_details(self, email_data: Dict) -> Dict:
        """Extract meeting details using Gemini."""
        if not self.gemini_model:
            return {
                'meeting_type': 'call',
                'duration': 60,
                'purpose': 'Meeting discussion',
                'urgency': 'medium'
            }
        
        try:
            subject = email_data.get('subject', '')[:100]
            body = (email_data.get('body', '') or email_data.get('snippet', ''))[:300]
            
            prompt = f"""Extract meeting details as JSON:

{{"meeting_type": "call/in-person/video", "duration": minutes, "purpose": "brief description", "urgency": "high/medium/low"}}

Email:
Subject: {subject}
Content: {body}

JSON only:"""

            response = self.gemini_model.generate_content(prompt)
            result = response.text.strip()
            
            # Clean up the response to extract JSON
            import json
            if result.startswith('```json'):
                result = result[7:-3]
            elif result.startswith('```'):
                result = result[3:-3]
            
            details = json.loads(result)
            return details
            
        except Exception as e:
            print(f"Meeting details extraction failed: {e}")
            return {
                'meeting_type': 'call',
                'duration': 60,
                'purpose': 'Meeting discussion',
                'urgency': 'medium'
            }