#!/usr/bin/env python3
"""Debug script to trace newsletter filtering issue."""

import sys
import os
sys.path.append('.')

from email_assistant.ollama_agents import OllamaEmailCategorizerAgent
from email_assistant.telegram_bot import SmartEmailFilter
from dotenv import load_dotenv

load_dotenv()

def test_full_pipeline():
    """Test the complete email processing pipeline."""
    
    print("🔍 DEBUGGING NEWSLETTER FILTERING PIPELINE")
    print("=" * 60)
    
    # Initialize components
    categorizer = OllamaEmailCategorizerAgent()
    filter_agent = SmartEmailFilter()
    
    # Test emails from your screenshots
    test_emails = [
        {
            'id': 'test_1',
            'subject': 'Live Event: How to Create a Not-Basic College Application',
            'sender': 'Ethan Sawyer <info@collegeessayguy.com>',
            'snippet': 'Five practical tips College Essay Guy Logo Hi Favour, Sometimes the best way to know what to do is to explore what not to do. By avoiding the common m...',
            'body': 'Newsletter content with tips and advice...'
        },
        {
            'id': 'test_2',
            'subject': 'Issue 288: Cowboys and heroes of developments', 
            'sender': 'Stack Overflow <do-not-reply@hello.stackoverflow.email>',
            'snippet': 'The origins of skulduggery, giving kids scissors, and wasting time',
            'body': 'Technical newsletter content...'
        },
        {
            'id': 'test_3',
            'subject': 'your silly idea',
            'sender': 'Pat @ Starter Story <pat@starterstory.com>',
            'snippet': 'Read time: 1 min. 18 sec. I talked to a founder the other day who made me laugh. He said when he just started out, everyone told him his idea was sill...',
            'body': 'Personal business email content...'
        }
    ]
    
    for i, email in enumerate(test_emails, 1):
        print(f"\n📧 EMAIL {i}: {email['subject']}")
        print("-" * 50)
        
        # Step 1: AI Categorization
        print("STEP 1: AI Categorization")
        category = categorizer.categorize_email(email)
        email['ai_category'] = category
        print(f"   Final AI Category: {category}")
        
        # Step 2: Meeting Detection (simulated)
        subject_lower = email['subject'].lower()
        body_lower = email.get('body', '').lower()
        meeting_keywords = ['meeting', 'call', 'conference', 'zoom', 'teams', 'webinar', 'appointment', 'schedule', 'calendar', 'invite', 'invitation']
        is_meeting = any(keyword in subject_lower or keyword in body_lower for keyword in meeting_keywords)
        email['is_meeting_request'] = is_meeting
        print(f"   Meeting Detection: {is_meeting}")
        
        # Step 3: Smart Filter Decision
        print("STEP 2: Smart Filter Decision")
        should_notify = filter_agent.should_notify(email)
        print(f"   Filter Decision: {'✅ NOTIFY' if should_notify else '❌ BLOCK'}")
        
        # Step 4: Simulation Result
        print("STEP 3: Expected Behavior")
        if should_notify:
            print(f"   📱 Would send Telegram notification: '{category} Email'")
        else:
            print(f"   🔇 Would NOT send notification (filtered out)")
        
        print()

if __name__ == "__main__":
    test_full_pipeline()