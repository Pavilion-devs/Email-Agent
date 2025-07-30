"""AI Agents for email processing using LangChain and OpenAI."""

import os
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.schema import HumanMessage, SystemMessage

class EmailCategorizerAgent:
    """Agent for categorizing emails into predefined categories."""
    
    def __init__(self, api_key: str = None):
        """Initialize the categorizer agent."""
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.llm = ChatOpenAI(
            temperature=0.1,
            openai_api_key=api_key,
            model_name="gpt-4"
        )
        
        self.categories = os.getenv('EMAIL_CATEGORIES', 'Important,Newsletters,Promotions,Meetings,Personal').split(',')
        
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""You are an expert email categorizer. Analyze the email content and categorize it into exactly one of these categories: {', '.join(self.categories)}.

Category definitions:
- Important: Urgent business matters, project updates, client communications, deadlines, work-related tasks
- Newsletters: Weekly/monthly updates, tech industry news, subscriptions, regular informational emails
- Promotions: Sales offers, discounts, marketing emails, advertisements, limited time offers
- Meetings: Meeting requests, calendar invites, scheduling discussions, availability inquiries
- Personal: Personal communications, family, friends, birthday wishes, non-work related

Rules:
1. Look at the subject line first for clear indicators
2. Consider the sender domain and context
3. Respond with ONLY the category name
4. Be very specific about promotions (look for "offer", "discount", "sale")
5. Be very specific about meetings (look for "meeting", "schedule", "availability")"""),
            HumanMessage(content="Subject: {subject}\nSender: {sender}\nSnippet: {snippet}")
        ])
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def categorize_email(self, email_data: Dict) -> str:
        """Categorize a single email."""
        try:
            result = self.chain.invoke({
                "subject": email_data.get('subject', ''),
                "sender": email_data.get('sender', ''),
                "snippet": email_data.get('snippet', '')
            })
            
            category = result["text"].strip()
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
        
        self.llm = ChatOpenAI(
            temperature=0.7,
            openai_api_key=api_key,
            model_name="gpt-4"
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a professional email assistant. Generate appropriate email responses based on the original email content and context.

Guidelines:
- Keep responses concise and professional
- Match the tone of the original email
- Address the key points raised
- Include appropriate greeting and closing
- Do not make commitments without explicit instruction
- If the email requires scheduling, suggest checking availability
- If information is needed, ask specific questions

Generate only the email body content, no subject line."""),
            HumanMessage(content="Original Email:\nSubject: {subject}\nFrom: {sender}\nBody: {body}\n\nPlease generate an appropriate response:")
        ])
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def generate_response(self, email_data: Dict, context: str = "") -> str:
        """Generate a response to an email."""
        try:
            response = self.chain.invoke({
                "subject": email_data.get('subject', ''),
                "sender": email_data.get('sender', ''),
                "body": email_data.get('body', '') or email_data.get('snippet', ''),
                "context": context
            })
            
            return response["text"].strip()
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Thank you for your email. I'll review this and get back to you soon."
    
    def should_respond(self, email_data: Dict) -> bool:
        """Determine if an email should receive an auto-response."""
        try:
            decision_prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""Determine if this email should receive an automated response. 

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

Respond with only 'YES' or 'NO'."""),
                HumanMessage(content="Subject: {subject}\nSender: {sender}\nSnippet: {snippet}")
            ])
            
            decision_chain = LLMChain(llm=self.llm, prompt=decision_prompt)
            result = decision_chain.invoke({
                "subject": email_data.get('subject', ''),
                "sender": email_data.get('sender', ''),
                "snippet": email_data.get('snippet', '')
            })["text"].strip().upper()
            
            return result == 'YES'
            
        except Exception as e:
            print(f"Error determining response need: {e}")
            return False


class MeetingSchedulerAgent:
    """Agent for detecting meeting requests and suggesting times."""
    
    def __init__(self, api_key: str = None):
        """Initialize the scheduler agent."""
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.llm = ChatOpenAI(
            temperature=0.1,
            openai_api_key=api_key,
            model_name="gpt-4"
        )
        
        self.detection_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""Analyze the email to determine if it contains a meeting request or scheduling discussion.

Look for:
- Direct meeting requests ("let's schedule", "can we meet")
- Availability inquiries ("when are you free", "available times")
- Calendar invitations or scheduling language
- Discussion of meetings, calls, or appointments

Respond with 'YES' if the email is about scheduling/meetings, 'NO' otherwise."""),
            HumanMessage(content="Subject: {subject}\nSender: {sender}\nBody: {body}")
        ])
        
        self.details_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""Extract meeting details from this email and format as JSON.

Extract:
- meeting_type: type of meeting (call, in-person, video, etc.)
- duration: estimated duration in minutes (default 60)
- purpose: brief description of meeting purpose
- urgency: high/medium/low based on language used
- participants: list of mentioned participants (emails if available)

Format as JSON only, no other text."""),
            HumanMessage(content="Subject: {subject}\nSender: {sender}\nBody: {body}")
        ])
    
    def is_meeting_request(self, email_data: Dict) -> bool:
        """Check if email contains a meeting request."""
        try:
            chain = LLMChain(llm=self.llm, prompt=self.detection_prompt)
            result = chain.invoke({
                "subject": email_data.get('subject', ''),
                "sender": email_data.get('sender', ''),
                "body": email_data.get('body', '') or email_data.get('snippet', '')
            })["text"].strip().upper()
            
            return result == 'YES'
            
        except Exception as e:
            print(f"Error detecting meeting request: {e}")
            return False
    
    def extract_meeting_details(self, email_data: Dict) -> Dict:
        """Extract meeting details from email."""
        try:
            chain = LLMChain(llm=self.llm, prompt=self.details_prompt)
            result = chain.invoke({
                "subject": email_data.get('subject', ''),
                "sender": email_data.get('sender', ''),
                "body": email_data.get('body', '') or email_data.get('snippet', '')
            })["text"].strip()
            
            # Try to parse JSON response
            import json
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
            
            response_prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""Generate a professional email response for a meeting request with suggested times.

Include:
- Acknowledgment of the meeting request
- Suggested available times
- Request for confirmation
- Professional closing

Keep it concise and friendly."""),
                HumanMessage(content="""Original meeting request:
Subject: {subject}
From: {sender}

Suggested available times:
{times}

Generate an appropriate response:""")
            ])
            
            chain = LLMChain(llm=self.llm, prompt=response_prompt)
            response = chain.invoke({
                "subject": email_data.get('subject', ''),
                "sender": email_data.get('sender', ''),
                "times": times_text
            })["text"]
            
            return response.strip()
            
        except Exception as e:
            print(f"Error generating scheduling response: {e}")
            return f"Thank you for the meeting request. I have some availability and will get back to you with specific times soon."