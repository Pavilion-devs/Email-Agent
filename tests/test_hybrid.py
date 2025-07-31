"""Test script for hybrid agents with cost tracking."""

import os
from dotenv import load_dotenv
from email_assistant.hybrid_agents import HybridEmailCategorizerAgent, CostOptimizedResponderAgent, CostOptimizedMeetingAgent

# Load environment variables
load_dotenv()

# Sample test emails for hybrid testing
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
    },
    {
        'id': 'test6',
        'subject': 'Quarterly Report Discussion',
        'sender': 'colleague@work.com',
        'snippet': 'Can we schedule a meeting to discuss the quarterly report? I have some questions about the metrics.'
    },
    {
        'id': 'test7',
        'subject': 'Machine Learning Weekly - Issue #42',
        'sender': 'updates@mlweekly.com',
        'snippet': 'The latest in machine learning research, tools, and industry news. This week: transformer improvements and new datasets.'
    },
    {
        'id': 'test8',
        'subject': 'Flash Sale: 70% off everything!',
        'sender': 'deals@retailstore.com',
        'snippet': 'Our biggest sale of the year is here! Everything must go. Limited time offer expires at midnight.'
    }
]

def test_hybrid_categorization():
    """Test hybrid categorization with cost tracking."""
    print("🧪 Testing Hybrid Email Categorization")
    print("=" * 50)
    
    try:
        categorizer = HybridEmailCategorizerAgent()
        results = categorizer.categorize_batch(SAMPLE_EMAILS)
        
        print(f"\n📊 Detailed Results:")
        for i, result in enumerate(results, 1):
            print(f"\n--- Email {i} ---")
            print(f"Subject: {result['subject'][:50]}...")
            print(f"Category: {result['ai_category']}")
            print(f"Method: {result['categorization_method']}")
            print(f"Cost: ${result['processing_cost']:.4f}")
            
    except Exception as e:
        print(f"❌ Hybrid categorization test failed: {e}")

def test_cost_optimized_responses():
    """Test cost-optimized response generation."""
    print("\n🧪 Testing Cost-Optimized Response Generation")
    print("=" * 50)
    
    try:
        responder = CostOptimizedResponderAgent()
        
        for email in SAMPLE_EMAILS:
            should_respond = responder.should_respond(email)
            print(f"\nSubject: {email['subject'][:50]}...")
            print(f"Should respond: {should_respond}")
            
            if should_respond:
                response = responder.generate_response(email)
                print(f"Response preview: {response[:100]}...")
                
    except Exception as e:
        print(f"❌ Response generation test failed: {e}")

def test_meeting_detection():
    """Test cost-optimized meeting detection."""
    print("\n🧪 Testing Cost-Optimized Meeting Detection")
    print("=" * 50)
    
    try:
        scheduler = CostOptimizedMeetingAgent()
        
        for email in SAMPLE_EMAILS:
            is_meeting = scheduler.is_meeting_request(email)
            print(f"\nSubject: {email['subject'][:50]}...")
            print(f"Is meeting request: {is_meeting}")
            
            if is_meeting:
                details = scheduler.extract_meeting_details(email)
                print(f"Meeting details: {details}")
                
    except Exception as e:
        print(f"❌ Meeting detection test failed: {e}")

def run_all_tests():
    """Run all hybrid tests."""
    print("🚀 Starting Hybrid Email Assistant Tests")
    print("=" * 50)
    
    # Check if API keys are set
    if not os.getenv('GOOGLE_API_KEY'):
        print("⚠️  Google API key not found. Gemini features will be limited.")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OpenAI API key not found. Fallback features will be limited.")
    
    test_hybrid_categorization()
    test_cost_optimized_responses()
    test_meeting_detection()
    
    print("\n✅ All hybrid tests completed!")
    print("\n💡 Cost Optimization Features:")
    print("   • Rule-based filtering (free for ~80% of emails)")
    print("   • Gemini 1.5 Flash backup (~$0.0001 per email)")
    print("   • OpenAI fallback only when needed")
    print("   • Smart truncation to avoid token limits")
    
    print("\n🚀 Next steps:")
    print("1. Install dependencies: pip install google-generativeai")
    print("2. Run full system: python main.py")
    print("3. Check cost savings in output")

if __name__ == "__main__":
    run_all_tests()