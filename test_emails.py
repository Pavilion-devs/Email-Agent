"""Test script with sample emails to verify Smart Email Assistant functionality."""

import os
from dotenv import load_dotenv
from email_assistant.agents import EmailCategorizerAgent, EmailResponderAgent, MeetingSchedulerAgent

# Load environment variables from .env file
load_dotenv()

# Sample test emails
SAMPLE_EMAILS = [
    {
        'id': 'test1',
        'subject': 'Project Update - Q4 Marketing Campaign',
        'sender': 'sarah.johnson@company.com',
        'snippet': 'Hi team, I wanted to provide an update on our Q4 marketing campaign. We\'ve completed the initial research phase and are ready to move forward with creative development. Please review the attached timeline and let me know if you have any concerns.',
        'body': 'Hi team, I wanted to provide an update on our Q4 marketing campaign. We\'ve completed the initial research phase and are ready to move forward with creative development. The budget has been approved and we\'re on track to launch by November 15th. Please review the attached timeline and let me know if you have any concerns. Best regards, Sarah'
    },
    {
        'id': 'test2',
        'subject': 'Weekly Newsletter - Tech Industry Updates',
        'sender': 'newsletter@techdigust.com',
        'snippet': 'This week in tech: AI breakthroughs, new startup funding rounds, and the latest in cybersecurity. Plus exclusive interviews with industry leaders.',
        'body': 'This week in tech: AI breakthroughs, new startup funding rounds, and the latest in cybersecurity. Plus exclusive interviews with industry leaders. Don\'t miss our special feature on emerging technologies that will shape 2024.'
    },
    {
        'id': 'test3',
        'subject': 'Limited Time Offer - 50% Off Premium Plan',
        'sender': 'sales@softwarecompany.com',
        'snippet': 'Don\'t miss out! Get 50% off our premium plan this week only. Upgrade now and unlock advanced features that will boost your productivity.',
        'body': 'Don\'t miss out! Get 50% off our premium plan this week only. Upgrade now and unlock advanced features that will boost your productivity. This offer expires in 48 hours. Click here to upgrade now!'
    },
    {
        'id': 'test4',
        'subject': 'Meeting Request - Strategic Planning Session',
        'sender': 'mike.chen@company.com',
        'snippet': 'Hi, I\'d like to schedule a strategic planning session for next week. Do you have any availability on Tuesday or Wednesday afternoon? The meeting should take about 2 hours.',
        'body': 'Hi, I\'d like to schedule a strategic planning session for next week to discuss our roadmap for the next quarter. Do you have any availability on Tuesday or Wednesday afternoon? The meeting should take about 2 hours and we\'ll need to review the budget proposals. Please let me know what works best for your schedule. Thanks, Mike'
    },
    {
        'id': 'test5',
        'subject': 'Happy Birthday! 🎉',
        'sender': 'mom@family.com',
        'snippet': 'Happy birthday sweetheart! I hope you have a wonderful day. Can\'t wait to see you this weekend for the family dinner.',
        'body': 'Happy birthday sweetheart! I hope you have a wonderful day filled with joy and happiness. Can\'t wait to see you this weekend for the family dinner. I\'ve prepared your favorite cake! Love you lots, Mom'
    }
]

def test_categorization():
    """Test email categorization."""
    print("🧪 Testing Email Categorization")
    print("=" * 40)
    
    try:
        categorizer = EmailCategorizerAgent()
        
        for email in SAMPLE_EMAILS:
            category = categorizer.categorize_email(email)
            print(f"Subject: {email['subject'][:50]}...")
            print(f"Category: {category}")
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Categorization test failed: {e}")

def test_response_generation():
    """Test response generation."""
    print("\n🧪 Testing Response Generation")
    print("=" * 40)
    
    try:
        responder = EmailResponderAgent()
        
        for email in SAMPLE_EMAILS:
            should_respond = responder.should_respond(email)
            print(f"Subject: {email['subject'][:50]}...")
            print(f"Should respond: {should_respond}")
            
            if should_respond:
                response = responder.generate_response(email)
                print(f"Response preview: {response[:100]}...")
            
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Response generation test failed: {e}")

def test_meeting_detection():
    """Test meeting request detection."""
    print("\n🧪 Testing Meeting Detection")
    print("=" * 40)
    
    try:
        scheduler = MeetingSchedulerAgent()
        
        for email in SAMPLE_EMAILS:
            is_meeting = scheduler.is_meeting_request(email)
            print(f"Subject: {email['subject'][:50]}...")
            print(f"Is meeting request: {is_meeting}")
            
            if is_meeting:
                details = scheduler.extract_meeting_details(email)
                print(f"Meeting details: {details}")
            
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Meeting detection test failed: {e}")

def run_all_tests():
    """Run all tests."""
    print("🚀 Starting Smart Email Assistant Tests")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        return
    
    test_categorization()
    test_response_generation()
    test_meeting_detection()
    
    print("\n✅ All tests completed!")
    print("\nNext steps:")
    print("1. Set up Gmail API credentials (credentials.json)")
    print("2. Run: python main.py")
    print("3. Run dashboard: python main.py --dashboard")

if __name__ == "__main__":
    run_all_tests()