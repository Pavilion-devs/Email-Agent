"""Test script for Telegram bot integration."""

import os
from dotenv import load_dotenv
from email_assistant.telegram_bot import TelegramBot, SmartEmailFilter

# Load environment variables
load_dotenv()

def test_telegram_connection():
    """Test basic Telegram bot connection."""
    print("🤖 Testing Telegram Bot Connection")
    print("=" * 40)
    
    try:
        bot = TelegramBot()
        print("✅ Bot initialized successfully")
        
        # Test message sending
        test_message = """🧪 *Test Message*

This is a test message from your Smart Email Assistant bot!

If you receive this, your bot is working correctly. ✅

*Features ready:*
📱 Smart notifications
🤖 AI responses with Ollama  
📅 Meeting scheduling
✍️ Interactive buttons"""
        
        success = bot.send_message(test_message)
        if success:
            print("✅ Test message sent successfully!")
        else:
            print("❌ Failed to send test message")
            
    except Exception as e:
        print(f"❌ Bot test failed: {e}")

def test_smart_filter():
    """Test the smart email filter logic."""
    print("\n🔍 Testing Smart Email Filter")
    print("=" * 40)
    
    filter_agent = SmartEmailFilter()
    
    # Test emails
    test_emails = [
        {
            'subject': 'Action Required: Verify your account',
            'sender': 'security@bank.com',
            'ai_category': 'Important',
            'is_meeting_request': False
        },
        {
            'subject': 'Weekly Newsletter - Tech Updates',
            'sender': 'newsletter@tech.com',
            'ai_category': 'Newsletters', 
            'is_meeting_request': False
        },
        {
            'subject': 'Meeting Request - Project Discussion',
            'sender': 'colleague@work.com',
            'ai_category': 'Meetings',
            'is_meeting_request': True
        },
        {
            'subject': 'Flash Sale - 50% Off Everything',
            'sender': 'sales@store.com',
            'ai_category': 'Promotions',
            'is_meeting_request': False
        },
        {
            'subject': 'Submit Your Financial Documents',
            'sender': 'international@university.edu',
            'ai_category': 'Important',
            'is_meeting_request': False
        }
    ]
    
    for i, email in enumerate(test_emails, 1):
        should_notify = filter_agent.should_notify(email)
        priority = filter_agent.get_notification_priority(email)
        
        print(f"Email {i}: {email['subject'][:40]}...")
        print(f"   Category: {email['ai_category']}")
        print(f"   Notify: {'✅ YES' if should_notify else '❌ NO'}")
        print(f"   Priority: {priority}")
        print("-" * 40)

def test_notification_format():
    """Test notification message formatting."""
    print("\n📱 Testing Notification Formatting")
    print("=" * 40)
    
    try:
        bot = TelegramBot()
        
        # Sample important email
        sample_email = {
            'id': 'test_123',
            'subject': 'Action Required: Please verify your account within 24 hours',
            'sender': 'Security Team <security@bank.com>',
            'snippet': 'We noticed unusual activity on your account. Please click the link below to verify your identity and secure your account.',
            'ai_category': 'Important',
            'is_meeting_request': False,
            'date': '2025-01-31T15:30:00'
        }
        
        # Test notification sending
        success = bot.send_email_notification(sample_email, include_actions=True)
        
        if success:
            print("✅ Sample notification sent with interactive buttons!")
            print("   Check your Telegram to see the formatted message")
        else:
            print("❌ Failed to send sample notification")
            
    except Exception as e:
        print(f"❌ Notification test failed: {e}")

def show_setup_instructions():
    """Show setup instructions for Telegram bot."""
    print("\n📱 Telegram Bot Setup Instructions")
    print("=" * 50)
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env file")
        print("\n🔧 To create your Telegram bot:")
        print("1. Open Telegram and search for @BotFather")
        print("2. Send: /newbot")
        print("3. Choose name: Smart Email Assistant")
        print("4. Choose username: your_email_assistant_bot")
        print("5. Copy the token to your .env file")
        print("\nExample:")
        print("TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
    else:
        print(f"✅ Bot token configured: {bot_token[:10]}...")
    
    if not chat_id:
        print("\n⚠️  TELEGRAM_CHAT_ID not found in .env file")
        print("\n🔧 To get your chat ID:")
        print("1. Start your bot on Telegram")
        print("2. Send /start message")
        print("3. The bot will show your chat ID")
        print("4. Add it to your .env file")
        print("\nExample:")
        print("TELEGRAM_CHAT_ID=123456789")
    else:
        print(f"✅ Chat ID configured: {chat_id}")

def run_all_tests():
    """Run all Telegram bot tests."""
    print("🚀 Starting Telegram Bot Tests")
    print("=" * 50)
    
    show_setup_instructions()
    test_smart_filter()
    
    # Only run connection tests if bot token is configured
    if os.getenv('TELEGRAM_BOT_TOKEN'):
        test_telegram_connection()
        
        if os.getenv('TELEGRAM_CHAT_ID'):
            test_notification_format()
        else:
            print("\n💡 Configure TELEGRAM_CHAT_ID to test notifications")
    else:
        print("\n💡 Configure TELEGRAM_BOT_TOKEN to test bot connection")
    
    print("\n✅ All Telegram tests completed!")
    print("\n🚀 Next steps:")
    print("1. Create your Telegram bot with @BotFather")
    print("2. Add bot token and chat ID to .env")
    print("3. Run: python telegram_bot_server.py")
    print("4. Run email processing: python main.py")

if __name__ == "__main__":
    run_all_tests()