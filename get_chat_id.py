#!/usr/bin/env python3
"""Script to get your Telegram Chat ID."""

import os
import requests
from dotenv import load_dotenv

def get_chat_id():
    """Get the chat ID from recent messages."""
    load_dotenv()
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env file")
        return
    
    print("🔍 Looking for your Telegram Chat ID...")
    print(f"🤖 Bot: @mypavilion_bot")
    print("\n📱 Instructions:")
    print("1. Open Telegram and search for @mypavilion_bot")
    print("2. Send any message (like 'hello' or '/start')")
    print("3. Run this script again")
    print("\nChecking for recent messages...")
    
    try:
        api_url = f"https://api.telegram.org/bot{bot_token}"
        response = requests.get(f"{api_url}/getUpdates", timeout=10)
        
        if response.status_code == 200:
            updates = response.json().get('result', [])
            
            if updates:
                print(f"\n✅ Found {len(updates)} recent message(s)!")
                
                # Get the most recent message
                latest_update = updates[-1]
                
                if 'message' in latest_update:
                    chat_id = latest_update['message']['chat']['id']
                    username = latest_update['message']['chat'].get('username', 'Unknown')
                    first_name = latest_update['message']['chat'].get('first_name', 'Unknown')
                    
                    print(f"\n🎯 Your Chat ID: {chat_id}")
                    print(f"👤 Name: {first_name}")
                    print(f"📝 Username: @{username}" if username else "📝 Username: Not set")
                    
                    print(f"\n🔧 Add this to your .env file:")
                    print(f"TELEGRAM_CHAT_ID={chat_id}")
                    
                    # Update .env file automatically
                    try:
                        with open('.env', 'r') as f:
                            content = f.read()
                        
                        if 'TELEGRAM_CHAT_ID=your_telegram_chat_id_here' in content:
                            content = content.replace(
                                'TELEGRAM_CHAT_ID=your_telegram_chat_id_here',
                                f'TELEGRAM_CHAT_ID={chat_id}'
                            )
                            
                            with open('.env', 'w') as f:
                                f.write(content)
                            
                            print("✅ Automatically updated .env file!")
                            
                            # Send test message
                            test_message = f"""🎉 *Chat ID Setup Complete!*

Your Smart Email Assistant bot is now configured.

📱 *Your Details:*
• Chat ID: `{chat_id}`
• Name: {first_name}
• Username: @{username or 'Not set'}

✅ *Bot Status:* Ready to send notifications
🤖 *AI Engine:* Ollama llama3.2:3b (Local)
💰 *Cost:* 100% FREE

*Next Steps:*
1. Run: `python main.py` to process emails
2. Run: `python telegram_bot_server.py` for interactive features

The bot will only notify you about Important emails and Meeting requests to avoid spam! 🎯"""
                            
                            payload = {
                                'chat_id': chat_id,
                                'text': test_message,
                                'parse_mode': 'Markdown'
                            }
                            
                            test_response = requests.post(f"{api_url}/sendMessage", json=payload, timeout=10)
                            
                            if test_response.status_code == 200:
                                print("🎉 Test message sent to your Telegram!")
                            else:
                                print("⚠️  Chat ID found but test message failed")
                        
                    except Exception as e:
                        print(f"⚠️  Could not update .env file automatically: {e}")
                        print(f"Please manually add: TELEGRAM_CHAT_ID={chat_id}")
                    
                else:
                    print("❌ No message found in latest update")
            else:
                print("\n❌ No recent messages found")
                print("💡 Please send a message to @mypavilion_bot first")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    get_chat_id()