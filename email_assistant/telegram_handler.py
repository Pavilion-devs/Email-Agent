"""Telegram Bot Handler for processing callbacks and managing email actions."""

import os
import json
import time
import pickle
from typing import Dict, List, Optional
import requests
from datetime import datetime, timedelta
from .telegram_bot import TelegramBot, SmartEmailFilter
from .ollama_agents import OllamaEmailResponderAgent, OllamaMeetingSchedulerAgent
from .gmail_client import GmailClient
from .calendar_client import CalendarClient

class TelegramEmailHandler:
    """Handler for processing Telegram bot callbacks and managing email actions."""
    
    def __init__(self):
        """Initialize the Telegram handler."""
        self.bot = TelegramBot()
        self.filter = SmartEmailFilter()
        self.responder_agent = OllamaEmailResponderAgent()
        self.scheduler_agent = OllamaMeetingSchedulerAgent()
        
        # Initialize email clients
        try:
            self.gmail_client = GmailClient()
        except Exception as e:
            print(f"Warning: Gmail client not available: {e}")
            self.gmail_client = None
        
        try:
            self.calendar_client = CalendarClient()
        except Exception as e:
            print(f"Warning: Calendar client not available: {e}")
            self.calendar_client = None
        
        # Persistent storage for email data using pickle files
        self.cache_file = 'telegram_email_cache.pkl'
        self.responses_file = 'telegram_responses_cache.pkl'
        
        # Load existing cache data
        self.email_cache = self._load_cache(self.cache_file)
        self.pending_responses = self._load_cache(self.responses_file)
    
    def _load_cache(self, filename: str) -> dict:
        """Load cache data from pickle file."""
        try:
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    data = pickle.load(f)
                print(f"📂 Loaded {len(data)} items from {filename}")
                return data
        except Exception as e:
            print(f"⚠️  Could not load cache {filename}: {e}")
        return {}
    
    def _save_cache(self, data: dict, filename: str):
        """Save cache data to pickle file."""
        try:
            with open(filename, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"⚠️  Could not save cache {filename}: {e}")
    
    def process_important_emails(self, emails: List[Dict]) -> int:
        """Process emails and send notifications for important ones."""
        notification_count = 0
        
        print("\n📱 Processing emails for Telegram notifications...")
        
        for email in emails:
            if self.filter.should_notify(email):
                # Cache email data for callback handling
                email_id = email.get('id')
                self.email_cache[email_id] = email
                self._save_cache(self.email_cache, self.cache_file)
                
                # Send notification
                success = self.bot.send_email_notification(email, include_actions=True)
                if success:
                    notification_count += 1
                    priority = self.filter.get_notification_priority(email)
                    print(f"   📲 Sent {priority} priority notification: {email.get('subject', 'No Subject')[:40]}...")
        
        # No summary message needed for real-time processing
        
        return notification_count
    
    def start_polling(self):
        """Start polling for Telegram updates (callback handling)."""
        print("🤖 Starting Telegram bot callback polling...")
        
        last_update_id = 0
        
        while True:
            try:
                # Get updates from Telegram
                response = requests.get(
                    f"{self.bot.api_url}/getUpdates",
                    params={'offset': last_update_id + 1, 'timeout': 10}
                )
                
                if response.status_code == 200:
                    updates = response.json().get('result', [])
                    
                    for update in updates:
                        last_update_id = update['update_id']
                        
                        # Handle callback queries (button presses)
                        if 'callback_query' in update:
                            self._handle_callback_query(update['callback_query'])
                        
                        # Handle regular messages (for chat ID discovery)
                        elif 'message' in update:
                            self._handle_message(update['message'])
                
                # Small delay to prevent hammering the API
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n⛔ Stopping Telegram bot polling...")
                break
            except Exception as e:
                print(f"❌ Polling error: {e}")
                time.sleep(5)  # Wait longer on error
    
    def _handle_callback_query(self, callback_query: Dict):
        """Handle button press callbacks."""
        callback_data = callback_query.get('data', '')
        query_id = callback_query.get('id')
        chat_id = callback_query['message']['chat']['id']
        
        print(f"📱 Received callback: {callback_data}")
        
        # Parse callback data
        parts = callback_data.split('_')
        action = parts[0]
        email_id = parts[1] if len(parts) > 1 else None
        
        # Debug: Check if email exists in cache
        if email_id:
            if email_id in self.email_cache:
                print(f"✅ Email {email_id} found in cache")
            else:
                print(f"❌ Email {email_id} NOT found in cache. Available IDs: {list(self.email_cache.keys())}")
                # Try to reload cache from file
                self.email_cache = self._load_cache(self.cache_file)
                if email_id in self.email_cache:
                    print(f"✅ Email {email_id} found after reloading cache")
                else:
                    print(f"❌ Email {email_id} still not found after reloading")
        
        # Answer the callback query first (removes loading state)
        self._answer_callback_query(query_id)
        
        # Route to appropriate handler
        if action == 'reply':
            self._handle_reply_action(email_id, chat_id)
        elif action == 'schedule':
            self._handle_schedule_action(email_id, chat_id)
        elif action == 'view':
            self._handle_view_action(email_id, chat_id)
        elif action == 'ignore':
            self._handle_ignore_action(email_id, chat_id)
        elif action == 'done':
            self._handle_done_action(email_id, chat_id)
        elif action == 'send':
            self._handle_send_action(email_id, chat_id)
        elif action == 'cancel':
            self._handle_cancel_action(email_id, chat_id)
        elif action == 'time':
            time_index = int(parts[2]) if len(parts) > 2 else 0
            self._handle_time_selection(email_id, time_index, chat_id)
        else:
            self.bot.send_message(f"❓ Unknown action: {action}")
    
    def _handle_message(self, message: Dict):
        """Handle regular text messages."""
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        if text == '/start':
            welcome_message = """🤖 *Smart Email Assistant Bot*

I'll send you notifications for important emails and help you manage them quickly.

*Features:*
📱 Smart notifications (Important emails only)
✍️ AI-generated responses
📅 Meeting scheduling
🔇 Noise filtering

*Commands:*
/start - Show this help
/status - Show bot status
/test - Send test notification

Your Chat ID: `{}`
Add this to your .env file if not already configured.""".format(chat_id)
            
            self.bot.send_message(welcome_message)
        
        elif text == '/status':
            status_message = f"""📊 *Bot Status*

🤖 Bot: Online ✅
📧 Gmail: {'✅' if self.gmail_client else '❌'}
📅 Calendar: {'✅' if self.calendar_client else '❌'}
🦙 Ollama: ✅ (Local AI)

📱 Chat ID: `{chat_id}`
🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            self.bot.send_message(status_message)
        
        elif text == '/test':
            # Send a test notification
            test_email = {
                'id': 'test_123',
                'subject': 'Test Notification - Smart Email Assistant',
                'sender': 'Test Bot <test@example.com>',
                'snippet': 'This is a test notification to verify your Telegram bot is working correctly.',
                'ai_category': 'Important',
                'is_meeting_request': False
            }
            
            self.email_cache['test_123'] = test_email
            self._save_cache(self.email_cache, self.cache_file)
            self.bot.send_email_notification(test_email, include_actions=True)
    
    def _answer_callback_query(self, query_id: str, text: str = "Processing..."):
        """Answer callback query to remove loading state."""
        try:
            requests.post(
                f"{self.bot.api_url}/answerCallbackQuery",
                json={'callback_query_id': query_id, 'text': text}
            )
        except Exception as e:
            print(f"Error answering callback query: {e}")
    
    def _handle_reply_action(self, email_id: str, chat_id: str):
        """Handle reply button press - generate AI response."""
        email_data = self.email_cache.get(email_id)
        if not email_data:
            self.bot.send_message("❌ Email data not found. Please try again.")
            return
        
        self.bot.send_message("🤖 Generating AI response with Ollama... This may take a moment.")
        
        try:
            # Generate response using Ollama
            response = self.responder_agent.generate_response(email_data)
            
            # Store for potential sending
            self.pending_responses[email_id] = response
            self._save_cache(self.pending_responses, self.responses_file)
            
            # Send preview
            self.bot.send_response_preview(email_data, response)
            
        except Exception as e:
            self.bot.send_message(f"❌ Error generating response: {str(e)}")
    
    def _handle_schedule_action(self, email_id: str, chat_id: str):
        """Handle schedule button press - suggest meeting times."""
        email_data = self.email_cache.get(email_id)
        if not email_data:
            self.bot.send_message("❌ Email data not found. Please try again.")
            return
        
        if not self.calendar_client:
            self.bot.send_message("❌ Calendar integration not available. Please set up calendar credentials.")
            return
        
        self.bot.send_message("📅 Checking calendar availability...")
        
        try:
            # Get meeting details
            meeting_details = self.scheduler_agent.extract_meeting_details(email_data)
            duration = meeting_details.get('duration', 60)
            
            # Get suggested times
            suggested_times = self.calendar_client.suggest_meeting_times(duration_minutes=duration)
            
            if suggested_times:
                self.bot.send_meeting_schedule_options(email_data, suggested_times)
            else:
                self.bot.send_message("❌ No available time slots found. Please suggest a custom time.")
                
        except Exception as e:
            self.bot.send_message(f"❌ Error checking calendar: {str(e)}")
    
    def _handle_view_action(self, email_id: str, chat_id: str):
        """Handle view full email action."""
        email_data = self.email_cache.get(email_id)
        if not email_data:
            self.bot.send_message("❌ Email data not found. Please try again.")
            return
        
        full_message = f"""📧 *Full Email Details*

👤 *From:* {email_data.get('sender', 'Unknown')}
📝 *Subject:* {email_data.get('subject', 'No Subject')}
📂 *Category:* {email_data.get('ai_category', 'Unknown')}
🕐 *Date:* {email_data.get('date', 'Unknown')}

📄 *Content:*
```
{email_data.get('body', email_data.get('snippet', 'No content available'))[:1000]}
```

🆔 *Email ID:* `{email_id}`"""
        
        self.bot.send_message(full_message)
    
    def _handle_ignore_action(self, email_id: str, chat_id: str):
        """Handle ignore action."""
        self.bot.send_success_message("ignored", "Email marked as ignored. No further action needed.")
        
        # Remove from cache to free memory
        if email_id in self.email_cache:
            del self.email_cache[email_id]
            self._save_cache(self.email_cache, self.cache_file)
    
    def _handle_done_action(self, email_id: str, chat_id: str):
        """Handle mark done action."""
        self.bot.send_success_message("saved", "Email marked as completed.")
        
        # Remove from cache
        if email_id in self.email_cache:
            del self.email_cache[email_id]
            self._save_cache(self.email_cache, self.cache_file)
    
    def _handle_send_action(self, email_id: str, chat_id: str):
        """Handle send response action."""
        email_data = self.email_cache.get(email_id)
        response = self.pending_responses.get(email_id)
        
        if not email_data or not response:
            self.bot.send_message("❌ Response data not found. Please try again.")
            return
        
        if not self.gmail_client:
            self.bot.send_message("❌ Gmail integration not available. Cannot send email.")
            return
        
        try:
            # Extract recipient email
            sender = email_data.get('sender', '')
            if '<' in sender:
                recipient_email = sender.split('<')[1].split('>')[0]
            else:
                recipient_email = sender
            
            # Send email
            subject = email_data.get('subject', 'No Subject')
            success = self.gmail_client.send_email(
                to=recipient_email,
                subject=f"Re: {subject}",
                body=response,
                reply_to_id=email_id
            )
            
            if success:
                self.bot.send_success_message("sent", f"Response sent to {recipient_email}")
                
                # Clean up
                if email_id in self.email_cache:
                    del self.email_cache[email_id]
                    self._save_cache(self.email_cache, self.cache_file)
                if email_id in self.pending_responses:
                    del self.pending_responses[email_id]
                    self._save_cache(self.pending_responses, self.responses_file)
            else:
                self.bot.send_message("❌ Failed to send email. Please try again.")
                
        except Exception as e:
            self.bot.send_message(f"❌ Error sending email: {str(e)}")
    
    def _handle_cancel_action(self, email_id: str, chat_id: str):
        """Handle cancel action."""
        self.bot.send_message("❌ Action cancelled.")
        
        # Clean up pending response
        if email_id in self.pending_responses:
            del self.pending_responses[email_id]
            self._save_cache(self.pending_responses, self.responses_file)
    
    def _handle_time_selection(self, email_id: str, time_index: int, chat_id: str):
        """Handle meeting time selection."""
        email_data = self.email_cache.get(email_id)
        if not email_data:
            self.bot.send_message("❌ Email data not found. Please try again.")
            return
        
        if not self.calendar_client:
            self.bot.send_message("❌ Calendar integration not available.")
            return
        
        try:
            # Get suggested times again
            meeting_details = self.scheduler_agent.extract_meeting_details(email_data)
            suggested_times = self.calendar_client.suggest_meeting_times(
                duration_minutes=meeting_details.get('duration', 60)
            )
            
            if time_index < len(suggested_times):
                selected_time = suggested_times[time_index]
                
                # Create calendar event
                start_time = datetime.fromisoformat(selected_time['start'])
                end_time = datetime.fromisoformat(selected_time['end'])
                
                # Extract attendee
                sender = email_data.get('sender', '')
                if '<' in sender:
                    attendee_email = sender.split('<')[1].split('>')[0]
                else:
                    attendee_email = sender
                
                event_id = self.calendar_client.create_event(
                    title=f"Meeting: {email_data.get('subject', 'Scheduled Meeting')}",
                    start_time=start_time,
                    end_time=end_time,
                    attendees=[attendee_email] if attendee_email else None,
                    description=f"Meeting scheduled via Smart Email Assistant\n\nOriginal email: {email_data.get('snippet', '')}"
                )
                
                if event_id:
                    # Generate and send confirmation response
                    response = self.scheduler_agent.generate_scheduling_response(email_data, [selected_time])
                    
                    # Store for potential sending
                    self.pending_responses[email_id] = response
                    self._save_cache(self.pending_responses, self.responses_file)
                    
                    self.bot.send_success_message("scheduled", f"""Meeting scheduled for {selected_time['formatted_start']}
                    
📅 Calendar event created
✍️ Response ready to send""")
                    
                    # Send response preview
                    self.bot.send_response_preview(email_data, response)
                else:
                    self.bot.send_message("❌ Failed to create calendar event.")
            else:
                self.bot.send_message("❌ Invalid time selection.")
                
        except Exception as e:
            self.bot.send_message(f"❌ Error scheduling meeting: {str(e)}")