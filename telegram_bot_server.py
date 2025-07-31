#!/usr/bin/env python3
"""
Standalone Telegram Bot Server for Smart Email Assistant
Run this separately to handle button callbacks and interactions.
"""

import os
import sys
from dotenv import load_dotenv
from email_assistant.telegram_handler import TelegramEmailHandler

def main():
    """Main function to start the Telegram bot server."""
    load_dotenv()
    
    print("🤖 Starting Smart Email Assistant Telegram Bot Server")
    print("=" * 60)
    
    # Check if required environment variables are set
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env file")
        print("\n📱 To set up your Telegram bot:")
        print("1. Message @BotFather on Telegram")
        print("2. Send: /newbot")
        print("3. Choose name: Smart Email Assistant")
        print("4. Choose username: your_email_assistant_bot")
        print("5. Copy the token to your .env file")
        print("\nExample .env entry:")
        print("TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
        return
    
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not chat_id:
        print("⚠️  TELEGRAM_CHAT_ID not found in .env file")
        print("💡 The bot will help you find your chat ID when you send /start")
        print("\nTo get your chat ID:")
        print("1. Start your bot on Telegram")
        print("2. Send /start message")
        print("3. The bot will show your chat ID")
        print("4. Add it to your .env file")
    
    try:
        # Initialize handler
        handler = TelegramEmailHandler()
        
        print("✅ Bot initialized successfully!")
        print(f"🤖 Bot token: {bot_token[:10]}...")
        print(f"💬 Chat ID: {chat_id or 'Not set - will be detected'}")
        print("\n📱 Bot Features:")
        print("   • Smart email notifications (Important emails only)")
        print("   • Interactive buttons (Reply/Schedule/Ignore)")
        print("   • AI-generated responses with Ollama")
        print("   • Meeting scheduling with Google Calendar")
        print("   • Email sending via Gmail API")
        
        print("\n🚀 Starting bot polling...")
        print("Press Ctrl+C to stop the bot")
        print("=" * 60)
        
        # Start polling for updates
        handler.start_polling()
        
    except KeyboardInterrupt:
        print("\n\n⛔ Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Bot error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your TELEGRAM_BOT_TOKEN in .env")
        print("2. Make sure Ollama is running: ollama serve")
        print("3. Verify Gmail API credentials are set up")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())