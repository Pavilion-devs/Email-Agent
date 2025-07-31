"""Telegram Bot for Smart Email Assistant notifications."""

import os
import json
import asyncio
from typing import Dict, List, Optional
import requests
from datetime import datetime

class TelegramBot:
    """Telegram bot for sending smart email notifications."""
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        """Initialize Telegram bot."""
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required in .env file")
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Test connection
        if not self._test_connection():
            print("⚠️  Warning: Could not connect to Telegram Bot API")
    
    def _test_connection(self) -> bool:
        """Test if bot token is valid."""
        try:
            response = requests.get(f"{self.api_url}/getMe", timeout=5)
            if response.status_code == 200:
                bot_info = response.json()
                print(f"✅ Connected to Telegram bot: @{bot_info['result']['username']}")
                return True
            else:
                print(f"❌ Telegram bot connection failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Telegram connection error: {e}")
            return False
    
    def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """Send a simple text message."""
        if not self.chat_id:
            print("⚠️  No TELEGRAM_CHAT_ID configured. Message not sent.")
            return False
        
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(f"{self.api_url}/sendMessage", json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"📱 Message sent to Telegram successfully")
                return True
            else:
                print(f"❌ Failed to send Telegram message: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Telegram send error: {e}")
            return False
    
    def send_email_notification(self, email_data: Dict, include_actions: bool = True) -> bool:
        """Send a smart email notification with action buttons."""
        
        # Format the notification message
        message = self._format_email_notification(email_data)
        
        if include_actions:
            # Add inline keyboard with action buttons
            return self._send_with_inline_keyboard(message, email_data)
        else:
            return self.send_message(message)
    
    def _format_email_notification(self, email_data: Dict) -> str:
        """Format email data into a clean notification message."""
        subject = email_data.get('subject', 'No Subject')[:100]
        sender = email_data.get('sender', 'Unknown Sender')
        category = email_data.get('ai_category', 'Unknown')
        snippet = email_data.get('snippet', '')[:150]
        
        # Extract sender name/email
        if '<' in sender:
            sender_name = sender.split('<')[0].strip().strip('"')
            sender_email = sender.split('<')[1].split('>')[0]
        else:
            sender_name = sender
            sender_email = sender
        
        # Category emoji mapping
        category_emojis = {
            'Important': '🚨',
            'Meetings': '📅',
            'Promotions': '🎯',
            'Newsletters': '📰',
            'Personal': '👤'
        }
        
        emoji = category_emojis.get(category, '📧')
        
        # Determine urgency
        is_urgent = any(word in subject.lower() for word in ['urgent', 'action required', 'deadline', 'expires'])
        urgency_indicator = '⚡ URGENT' if is_urgent else ''
        
        # Build message
        message = f"""{emoji} *{category} Email* {urgency_indicator}
        
📬 *From:* {sender_name}
📧 {sender_email}

📝 *Subject:* {subject}

💬 *Preview:* {snippet}...

🕐 *Received:* {datetime.now().strftime('%H:%M')}"""
        
        return message
    
    def _send_with_inline_keyboard(self, message: str, email_data: Dict) -> bool:
        """Send message with inline action buttons."""
        if not self.chat_id:
            return self.send_message(message)
        
        email_id = email_data.get('id', 'unknown')
        is_meeting = email_data.get('is_meeting_request', False)
        
        # Create inline keyboard based on email type
        keyboard = []
        
        if is_meeting:
            keyboard = [
                [
                    {"text": "📅 Schedule", "callback_data": f"schedule_{email_id}"},
                    {"text": "✍️ Reply", "callback_data": f"reply_{email_id}"}
                ],
                [
                    {"text": "👀 View Full", "callback_data": f"view_{email_id}"},
                    {"text": "🔇 Ignore", "callback_data": f"ignore_{email_id}"}
                ]
            ]
        else:
            keyboard = [
                [
                    {"text": "✍️ Reply", "callback_data": f"reply_{email_id}"},
                    {"text": "👀 View Full", "callback_data": f"view_{email_id}"}
                ],
                [
                    {"text": "✅ Mark Done", "callback_data": f"done_{email_id}"},
                    {"text": "🔇 Ignore", "callback_data": f"ignore_{email_id}"}
                ]
            ]
        
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown',
                'reply_markup': {
                    'inline_keyboard': keyboard
                }
            }
            
            response = requests.post(f"{self.api_url}/sendMessage", json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"📱 Interactive notification sent successfully")
                return True
            else:
                print(f"❌ Failed to send interactive notification: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending interactive notification: {e}")
            return False
    
    def send_response_preview(self, email_data: Dict, generated_response: str) -> bool:
        """Send a preview of the generated response for approval."""
        subject = email_data.get('subject', 'No Subject')[:50]
        sender = email_data.get('sender', 'Unknown')
        
        message = f"""✍️ *Generated Response Preview*

📧 *Replying to:* {subject}
👤 *To:* {sender}

📝 *Generated Response:*
```
{generated_response[:800]}...
```

*Do you want to send this response?*"""
        
        email_id = email_data.get('id', 'unknown')
        
        keyboard = [
            [
                {"text": "✅ Send Response", "callback_data": f"send_{email_id}"},
                {"text": "✏️ Edit Response", "callback_data": f"edit_{email_id}"}
            ],
            [
                {"text": "❌ Cancel", "callback_data": f"cancel_{email_id}"}
            ]
        ]
        
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown',
                'reply_markup': {
                    'inline_keyboard': keyboard
                }
            }
            
            response = requests.post(f"{self.api_url}/sendMessage", json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error sending response preview: {e}")
            return False
    
    def send_meeting_schedule_options(self, email_data: Dict, suggested_times: List[Dict]) -> bool:
        """Send meeting scheduling options."""
        subject = email_data.get('subject', 'No Subject')[:50]
        
        times_text = "\n".join([
            f"• {i+1}. {time['formatted_start']}"
            for i, time in enumerate(suggested_times[:3])
        ])
        
        message = f"""📅 *Meeting Scheduling Options*

📧 *For:* {subject}

⏰ *Suggested Times:*
{times_text}

*Which time works best for you?*"""
        
        email_id = email_data.get('id', 'unknown')
        
        # Create buttons for each time slot
        keyboard = []
        for i, time in enumerate(suggested_times[:3]):
            keyboard.append([
                {"text": f"📅 {time['formatted_start']}", "callback_data": f"time_{email_id}_{i}"}
            ])
        
        keyboard.append([
            {"text": "📝 Suggest Different Time", "callback_data": f"custom_time_{email_id}"},
            {"text": "❌ Cancel", "callback_data": f"cancel_{email_id}"}
        ])
        
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown',
                'reply_markup': {
                    'inline_keyboard': keyboard
                }
            }
            
            response = requests.post(f"{self.api_url}/sendMessage", json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error sending meeting options: {e}")
            return False
    
    def send_success_message(self, action: str, details: str = "") -> bool:
        """Send a success confirmation message."""
        emojis = {
            'sent': '✅',
            'scheduled': '📅',
            'ignored': '🔇',
            'saved': '💾'
        }
        
        emoji = emojis.get(action, '✅')
        
        message = f"""{emoji} *Action Completed*

*Status:* {action.title()} successfully
{details}

*Time:* {datetime.now().strftime('%H:%M:%S')}"""
        
        return self.send_message(message)
    
    def get_chat_id_from_message(self) -> Optional[str]:
        """Helper method to get chat ID - for initial setup."""
        try:
            response = requests.get(f"{self.api_url}/getUpdates", timeout=5)
            if response.status_code == 200:
                updates = response.json().get('result', [])
                if updates:
                    latest_update = updates[-1]
                    chat_id = latest_update['message']['chat']['id']
                    print(f"💡 Your Telegram Chat ID: {chat_id}")
                    print(f"   Add this to your .env file: TELEGRAM_CHAT_ID={chat_id}")
                    return str(chat_id)
        except Exception as e:
            print(f"Error getting chat ID: {e}")
        
        return None


class SmartEmailFilter:
    """Filter emails to determine which ones should trigger Telegram notifications."""
    
    def __init__(self):
        """Initialize the smart filter."""
        self.notification_categories = ['Important', 'Meetings']
        self.urgent_keywords = ['urgent', 'action required', 'deadline', 'expires', 'verify', 'security']
    
    def should_notify(self, email_data: Dict) -> bool:
        """Determine if this email should trigger a Telegram notification."""
        
        category = email_data.get('ai_category', '')
        subject = email_data.get('subject', '').lower()
        sender = email_data.get('sender', '').lower()
        is_meeting = email_data.get('is_meeting_request', False)
        
        # Always notify for Important emails
        if category == 'Important':
            return True
        
        # Always notify for Meeting requests
        if is_meeting or category == 'Meetings':
            return True
        
        # Notify for urgent emails regardless of category
        if any(keyword in subject for keyword in self.urgent_keywords):
            return True
        
        # Notify for university/education emails (these are often time-sensitive)
        if any(domain in sender for domain in ['.edu', 'university', 'college', 'school']):
            return True
        
        # Don't notify for newsletters, promotions, or personal (unless they meet above criteria)
        return False
    
    def get_notification_priority(self, email_data: Dict) -> str:
        """Get notification priority level."""
        subject = email_data.get('subject', '').lower()
        category = email_data.get('ai_category', '')
        
        # High priority
        if any(keyword in subject for keyword in ['urgent', 'deadline', 'expires today', 'action required']):
            return 'high'
        
        # Medium priority
        if category in ['Important', 'Meetings'] or email_data.get('is_meeting_request'):
            return 'medium'
        
        # Low priority
        return 'low'