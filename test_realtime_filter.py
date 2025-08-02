#!/usr/bin/env python3
"""Test real-time email processing pipeline to debug filtering issues."""

import sys
import os
sys.path.append('.')

from email_assistant.realtime_monitor import RealTimeEmailMonitor
from email_assistant.telegram_handler import TelegramEmailHandler
from email_assistant.ollama_agents import OllamaEmailCategorizerAgent
from dotenv import load_dotenv

load_dotenv()

def test_realtime_pipeline():
    """Test the complete real-time processing pipeline."""
    
    print("🔍 TESTING REAL-TIME EMAIL PROCESSING PIPELINE")
    print("=" * 60)
    
    # Initialize components like the real-time monitor does
    try:
        from email_assistant.gmail_client import GmailClient
        gmail_client = GmailClient()
        print("✅ Gmail client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Gmail client: {e}")
        return
    
    try:
        telegram_handler = TelegramEmailHandler()
        print("✅ Telegram handler initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Telegram handler: {e}")
        return
    
    try:
        categorizer_agent = OllamaEmailCategorizerAgent()
        print("✅ Ollama categorizer initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Ollama agent: {e}")
        return
    
    # Test the exact pipeline that real-time monitor uses
    print("\n📧 Testing email processing pipeline...")
    
    # Create test emails (including the problematic one)
    test_emails = [
        {
            'id': 'test_realtime_1',
            'subject': 'Top of the day',
            'sender': 'Kamiye <kamiye669@gmail.com>',
            'snippet': '31 July Which will you be? The good news is we\'ve got ways for you to be both. We don\'t mind being like Smokey Bear this week by saying, &quot...',
            'body': 'Promotional content about climate change and efficiency...',
            'date': '2024-07-31T22:38:00Z'
        },
        {
            'id': 'test_realtime_2',
            'subject': 'Important Meeting Request',
            'sender': 'colleague@company.com',
            'snippet': 'Hi, can we schedule a meeting to discuss the project?',
            'body': 'Hi, can we schedule a meeting to discuss the project? Let me know your availability.',
            'date': '2024-07-31T22:39:00Z'
        }
    ]
    
    # Process emails exactly like the real-time monitor does
    categorized_emails = []
    
    for email in test_emails:
        try:
            print(f"\n📧 Processing: {email['subject']}")
            
            # Step 1: AI Categorization (like real-time monitor)
            category = categorizer_agent.categorize_email(email)
            email['ai_category'] = category
            print(f"   📂 AI Category: {category}")
            
            # Step 2: Meeting Detection (like real-time monitor)
            subject_lower = email['subject'].lower()
            body_lower = email.get('body', '').lower()
            meeting_keywords = ['meeting', 'call', 'conference', 'zoom', 'teams', 'webinar', 'appointment', 'schedule', 'calendar', 'invite', 'invitation']
            is_meeting = any(keyword in subject_lower or keyword in body_lower for keyword in meeting_keywords)
            email['is_meeting_request'] = is_meeting
            print(f"   📅 Meeting Request: {is_meeting}")
            
            categorized_emails.append(email)
            
        except Exception as e:
            print(f"❌ Error processing email: {e}")
            # Add with default category like real-time monitor does
            email['ai_category'] = 'Important'
            email['is_meeting_request'] = False
            categorized_emails.append(email)
    
    # Step 3: Send notifications (like real-time monitor)
    print(f"\n📱 Processing {len(categorized_emails)} emails for notifications...")
    
    notification_count = telegram_handler.process_important_emails(categorized_emails)
    
    print(f"\n📊 RESULTS:")
    print(f"   Total emails processed: {len(categorized_emails)}")
    print(f"   Notifications sent: {notification_count}")
    print(f"   Emails filtered out: {len(categorized_emails) - notification_count}")
    
    # Show detailed results
    for email in categorized_emails:
        category = email.get('ai_category', 'Unknown')
        subject = email.get('subject', 'No Subject')[:40]
        should_notify = telegram_handler.filter.should_notify(email)
        
        status = "✅ NOTIFY" if should_notify else "❌ BLOCK"
        print(f"   {status} - {subject}... ({category})")

if __name__ == "__main__":
    test_realtime_pipeline() 