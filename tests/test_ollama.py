"""Test script for Ollama-based agents."""

import os
from dotenv import load_dotenv
from email_assistant.ollama_agents import OllamaEmailCategorizerAgent, OllamaEmailResponderAgent, OllamaMeetingSchedulerAgent

# Load environment variables
load_dotenv()

# Sample test emails for Ollama testing
SAMPLE_EMAILS = [
    {
        'id': 'test1',
        'subject': 'Limited Time Offer - 50% Off Premium Plan',
        'sender': 'sales@softwarecompany.com',
        'snippet': 'Don\'t miss out! Get 50% off our premium plan this week only. Upgrade now and unlock advanced features.'
    },
    {
        'id': 'test2', 
        'subject': 'Weekly Newsletter - Tech Industry Updates',
        'sender': 'newsletter@techdigest.com',
        'snippet': 'This week in tech: AI breakthroughs, new startup funding rounds, and the latest in cybersecurity.'
    },
    {
        'id': 'test3',
        'subject': 'Meeting Request - Strategic Planning Session',
        'sender': 'mike.chen@company.com',
        'snippet': 'Hi, I\'d like to schedule a strategic planning session for next week. Do you have any availability on Tuesday or Wednesday afternoon?'
    },
    {
        'id': 'test4',
        'subject': 'Action Required: Please verify your account',
        'sender': 'security@bankingsite.com',
        'snippet': 'We noticed unusual activity on your account. Please click here to verify your identity within 24 hours.'
    },
    {
        'id': 'test5',
        'subject': 'Happy Birthday! 🎉',
        'sender': 'mom@family.com',
        'snippet': 'Happy birthday sweetheart! I hope you have a wonderful day. Can\'t wait to see you this weekend.'
    }
]

def test_ollama_categorization():
    """Test Ollama email categorization."""
    print("🦙 Testing Ollama Email Categorization")
    print("=" * 50)
    
    try:
        categorizer = OllamaEmailCategorizerAgent()
        
        for email in SAMPLE_EMAILS:
            print(f"\nSubject: {email['subject'][:50]}...")
            category = categorizer.categorize_email(email)
            print(f"Category: {category}")
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Ollama categorization test failed: {e}")

def test_ollama_responses():
    """Test Ollama response generation."""
    print("\n🦙 Testing Ollama Response Generation")
    print("=" * 50)
    
    try:
        responder = OllamaEmailResponderAgent()
        
        for email in SAMPLE_EMAILS:
            should_respond = responder.should_respond(email)
            print(f"\nSubject: {email['subject'][:50]}...")
            print(f"Should respond: {should_respond}")
            
            if should_respond:
                print("Generating response with Ollama...")
                response = responder.generate_response(email)
                print(f"Response preview: {response[:150]}...")
                
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Ollama response generation test failed: {e}")

def test_ollama_meetings():
    """Test Ollama meeting detection."""
    print("\n🦙 Testing Ollama Meeting Detection")
    print("=" * 50)
    
    try:
        scheduler = OllamaMeetingSchedulerAgent()
        
        for email in SAMPLE_EMAILS:
            is_meeting = scheduler.is_meeting_request(email)
            print(f"\nSubject: {email['subject'][:50]}...")
            print(f"Is meeting request: {is_meeting}")
            
            if is_meeting:
                print("Extracting meeting details with Ollama...")
                details = scheduler.extract_meeting_details(email)
                print(f"Meeting details: {details}")
                
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Ollama meeting detection test failed: {e}")

def run_all_tests():
    """Run all Ollama tests."""
    print("🚀 Starting Ollama Email Assistant Tests")
    print("=" * 60)
    print("🦙 Using llama3.2:3b running locally (100% FREE)")
    print("=" * 60)
    
    test_ollama_categorization()
    test_ollama_responses()
    test_ollama_meetings()
    
    print("\n✅ All Ollama tests completed!")
    print("\n💡 Benefits of Ollama:")
    print("   • 100% FREE - No API costs")
    print("   • No rate limits - Process unlimited emails")
    print("   • Privacy - All processing happens locally")
    print("   • Reliability - No internet dependency")
    print("   • Speed - Local processing is fast")
    
    print("\n🚀 Next steps:")
    print("1. Run full system: python main.py")
    print("2. Process all 50 emails for FREE")
    print("3. No more $4.50 bills! 💰")

if __name__ == "__main__":
    run_all_tests()