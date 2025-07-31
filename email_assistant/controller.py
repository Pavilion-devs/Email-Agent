"""Main Controller for orchestrating email assistant agents."""

import os
import json
from datetime import datetime
from typing import List, Dict, Tuple
from .email_fetcher import EmailFetcher
from .ollama_agents import OllamaEmailCategorizerAgent, OllamaEmailResponderAgent, OllamaMeetingSchedulerAgent
from .telegram_handler import TelegramEmailHandler
from .gmail_client import GmailClient
from .calendar_client import CalendarClient

class EmailAssistantController:
    """Main controller that orchestrates all email assistant components."""
    
    def __init__(self):
        """Initialize the controller with all components."""
        print("Initializing Smart Email Assistant...")
        
        # Initialize components
        self.email_fetcher = EmailFetcher()
        self.categorizer_agent = OllamaEmailCategorizerAgent()
        self.responder_agent = OllamaEmailResponderAgent()
        self.scheduler_agent = OllamaMeetingSchedulerAgent()
        
        # Initialize Telegram integration
        try:
            self.telegram_handler = TelegramEmailHandler()
            print("📱 Telegram integration enabled")
        except Exception as e:
            print(f"⚠️  Telegram integration disabled: {e}")
            self.telegram_handler = None
        
        # Initialize API clients
        self.gmail_client = self.email_fetcher.gmail_client
        try:
            self.calendar_client = CalendarClient()
        except FileNotFoundError:
            print("Warning: Calendar credentials not found. Meeting scheduling will be limited.")
            self.calendar_client = None
        
        # Configuration
        self.auto_send = os.getenv('AUTO_SEND', 'false').lower() == 'true'
        self.demo_mode = os.getenv('DEMO_MODE', 'true').lower() == 'true'
        
        print("✅ Smart Email Assistant initialized successfully!")
    
    def run(self):
        """Main execution flow for the email assistant."""
        print("\n🚀 Starting Smart Email Assistant workflow...")
        
        # Step 1: Fetch emails
        emails = self._fetch_emails()
        
        if not emails:
            print("No emails found to process.")
            return
        
        # Step 2: Process emails
        results = self._process_emails(emails)
        
        # Step 3: Generate summary
        self._generate_summary(results)
        
        # Step 4: Execute actions (if auto_send is enabled)
        if self.auto_send:
            self._execute_actions(results)
    
    def _fetch_emails(self) -> List[Dict]:
        """Fetch emails for processing."""
        print("\n📧 Fetching emails...")
        
        # Fetch recent emails
        emails = self.email_fetcher.fetch_recent_emails()
        
        if emails:
            summary = self.email_fetcher.get_email_summary(emails)
            print(f"📊 Email Summary:")
            print(f"   Total: {summary['total']}")
            print(f"   Unread: {summary['unread']}")
            print(f"   Top senders: {', '.join(summary['senders'][:3])}")
        
        return emails
    
    def _process_emails(self, emails: List[Dict]) -> List[Dict]:
        """Process emails through all agents."""
        print(f"\n🤖 Processing {len(emails)} emails through AI agents...")
        
        results = []
        
        for i, email in enumerate(emails, 1):
            print(f"\n--- Processing email {i}/{len(emails)} ---")
            print(f"Subject: {email.get('subject', 'No Subject')[:60]}...")
            print(f"From: {email.get('sender', 'Unknown')}")
            
            # Prepare email for processing
            processed_email = self.email_fetcher.prepare_email_for_processing(email)
            
            # Step 1: Categorize email
            category = self.categorizer_agent.categorize_email(processed_email)
            processed_email['ai_category'] = category
            processed_email['categorization_method'] = 'ollama-local'
            processed_email['processing_cost'] = 0.0  # FREE!
            
            print(f"📂 Category: {category} (ollama-local)")
            print(f"💰 Cost: FREE 🦙")
            
            # Step 2: Check if meeting request
            is_meeting = self.scheduler_agent.is_meeting_request(processed_email)
            processed_email['is_meeting_request'] = is_meeting
            
            if is_meeting:
                print("📅 Meeting request detected!")
                meeting_details = self.scheduler_agent.extract_meeting_details(processed_email)
                processed_email['meeting_details'] = meeting_details
                
                # Suggest meeting times if calendar client available
                if self.calendar_client:
                    suggested_times = self.calendar_client.suggest_meeting_times(
                        duration_minutes=meeting_details.get('duration', 60)
                    )
                    processed_email['suggested_times'] = suggested_times
                    print(f"⏰ Suggested {len(suggested_times)} available time slots")
            
            # Step 3: Check if should respond
            should_respond = self.responder_agent.should_respond(processed_email)
            processed_email['should_respond'] = should_respond
            
            if should_respond:
                print("✍️ Generating response...")
                if is_meeting and self.calendar_client and processed_email.get('suggested_times'):
                    # Generate meeting response with suggested times
                    response = self.scheduler_agent.generate_scheduling_response(
                        processed_email, 
                        processed_email['suggested_times']
                    )
                else:
                    # Generate regular response
                    response = self.responder_agent.generate_response(processed_email)
                
                processed_email['generated_response'] = response
                print(f"📝 Response generated ({len(response)} characters)")
            
            results.append(processed_email)
        
        return results
    
    def _generate_summary(self, results: List[Dict]):
        """Generate and display processing summary."""
        print(f"\n📋 PROCESSING SUMMARY")
        print("=" * 50)
        
        # Category breakdown
        categories = {}
        meeting_count = 0
        response_count = 0
        
        for result in results:
            category = result.get('ai_category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
            
            if result.get('is_meeting_request'):
                meeting_count += 1
            
            if result.get('should_respond'):
                response_count += 1
        
        print(f"📊 Categories:")
        for category, count in sorted(categories.items()):
            print(f"   {category}: {count}")
        
        print(f"\n📅 Meeting requests detected: {meeting_count}")
        print(f"✍️ Emails requiring responses: {response_count}")
        
        # Send Telegram notifications for important emails
        if self.telegram_handler:
            try:
                notification_count = self.telegram_handler.process_important_emails(results)
                print(f"📱 Telegram notifications sent: {notification_count}")
            except Exception as e:
                print(f"❌ Telegram notification error: {e}")
        
        # Show detailed results for demo
        if self.demo_mode:
            self._show_demo_details(results)
    
    def _show_demo_details(self, results: List[Dict]):
        """Show detailed results for demo purposes."""
        print(f"\n🎬 DEMO DETAILS")
        print("=" * 50)
        
        for i, result in enumerate(results[:5], 1):  # Show first 5 for demo
            print(f"\n--- Email {i} ---")
            print(f"Subject: {result.get('subject', 'No Subject')}")
            print(f"Category: {result.get('ai_category', 'Unknown')}")
            print(f"Meeting Request: {'Yes' if result.get('is_meeting_request') else 'No'}")
            print(f"Needs Response: {'Yes' if result.get('should_respond') else 'No'}")
            
            if result.get('generated_response'):
                response = result['generated_response']
                print(f"Generated Response Preview: {response[:100]}...")
            
            if result.get('suggested_times'):
                print(f"Suggested Meeting Times:")
                for time in result['suggested_times'][:2]:
                    print(f"  - {time['formatted_start']}")
    
    def _execute_actions(self, results: List[Dict]):
        """Execute actions like sending responses and creating calendar events."""
        print(f"\n🚀 EXECUTING ACTIONS (Auto-send enabled)")
        print("=" * 50)
        
        sent_count = 0
        scheduled_count = 0
        labeled_count = 0
        
        for result in results:
            email_id = result.get('id')
            
            # Add category label
            if result.get('ai_category'):
                success = self.gmail_client.add_label(email_id, result['ai_category'])
                if success:
                    labeled_count += 1
            
            # Send response if needed
            if result.get('should_respond') and result.get('generated_response'):
                sender = result.get('sender', '')
                subject = result.get('subject', '')
                response = result['generated_response']
                
                # Extract sender email
                if '<' in sender:
                    sender_email = sender.split('<')[1].split('>')[0]
                else:
                    sender_email = sender
                
                success = self.gmail_client.send_email(
                    to=sender_email,
                    subject=f"Re: {subject}",
                    body=response,
                    reply_to_id=email_id
                )
                
                if success:
                    sent_count += 1
                    print(f"✅ Sent response to: {sender_email}")
            
            # Create calendar event for meetings
            if (result.get('is_meeting_request') and 
                self.calendar_client and 
                result.get('suggested_times')):
                
                event_id = self.calendar_client.create_meeting_from_email(
                    result, result['suggested_times']
                )
                
                if event_id:
                    scheduled_count += 1
                    print(f"📅 Created calendar event: {event_id}")
        
        print(f"\n📊 Actions completed:")
        print(f"   Labels added: {labeled_count}")
        print(f"   Responses sent: {sent_count}")
        print(f"   Meetings scheduled: {scheduled_count}")
    
    def process_single_email(self, email_id: str) -> Dict:
        """Process a single email by ID."""
        # This method can be used for testing or processing specific emails
        try:
            message = self.gmail_client.service.users().messages().get(
                userId='me', 
                id=email_id,
                format='full'
            ).execute()
            
            email_data = self.gmail_client._parse_message(message)
            processed_email = self.email_fetcher.prepare_email_for_processing(email_data)
            
            # Process through agents
            category = self.categorizer_agent.categorize_email(processed_email)
            processed_email['ai_category'] = category
            
            is_meeting = self.scheduler_agent.is_meeting_request(processed_email)
            processed_email['is_meeting_request'] = is_meeting
            
            should_respond = self.responder_agent.should_respond(processed_email)
            processed_email['should_respond'] = should_respond
            
            if should_respond:
                response = self.responder_agent.generate_response(processed_email)
                processed_email['generated_response'] = response
            
            return processed_email
            
        except Exception as e:
            print(f"Error processing email {email_id}: {e}")
            return {}