#!/usr/bin/env python3
"""Launcher for real-time email monitoring with Telegram bot."""

import os
import sys
import time
import signal
import threading
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_assistant.realtime_monitor import RealTimeEmailMonitor
from email_assistant.telegram_handler import TelegramEmailHandler

class RealTimeEmailSystem:
    """Combined real-time email monitoring and Telegram bot system."""
    
    def __init__(self):
        """Initialize the real-time system."""
        load_dotenv()
        
        self.monitor = None
        self.telegram_handler = None
        self.bot_thread = None
        self.is_running = False
    
    def start(self):
        """Start both real-time monitoring and Telegram bot polling."""
        print("🚀 Starting Real-Time Email System")
        print("=" * 50)
        
        # Initialize components
        try:
            # Create real-time monitor
            self.monitor = RealTimeEmailMonitor(polling_interval=30)
            print("✅ Real-time monitor initialized")
            
            # Create Telegram handler for callback processing
            self.telegram_handler = TelegramEmailHandler()
            print("✅ Telegram handler initialized")
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
        
        # Start both services
        self.is_running = True
        
        try:
            # Start real-time email monitoring
            self.monitor.start_monitoring()
            
            # Start Telegram bot polling in separate thread
            self.bot_thread = threading.Thread(
                target=self._start_telegram_polling, 
                daemon=True
            )
            self.bot_thread.start()
            
            print("\n🎉 Real-Time Email System is now running!")
            print("\n📊 System Status:")
            print("   📧 Real-time email monitoring: ✅ Active")
            print("   🤖 Telegram bot polling: ✅ Active") 
            print("   🦙 Ollama AI processing: ✅ Local")
            print("   💰 Cost: 🆓 100% FREE")
            print("\n🔔 Smart Notifications:")
            print("   ✅ Important emails only")
            print("   ✅ Meeting requests only")
            print("   ❌ Newsletters/Promotions filtered out")
            print("\n📱 Interactive Features:")
            print("   ✍️ AI-generated responses")
            print("   📅 Meeting scheduling")
            print("   👀 View full emails")
            print("\n⛔ Press Ctrl+C to stop")
            
            # Keep main thread alive
            while self.is_running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⛔ Received stop signal...")
            self.stop()
        except Exception as e:
            print(f"❌ System error: {e}")
            self.stop()
    
    def _start_telegram_polling(self):
        """Start Telegram bot polling in background thread."""
        try:
            print("🤖 Starting Telegram bot callback polling...")
            self.telegram_handler.start_polling()
        except Exception as e:
            print(f"❌ Telegram polling error: {e}")
    
    def stop(self):
        """Stop all services."""
        if not self.is_running:
            return
        
        print("\n🛑 Stopping Real-Time Email System...")
        self.is_running = False
        
        # Stop monitoring
        if self.monitor:
            self.monitor.stop_monitoring()
        
        # Stop Telegram polling (it will stop naturally when handler stops)
        print("⛔ Telegram bot polling will stop...")
        
        print("✅ All services stopped")
    
    def status(self):
        """Show system status."""
        if not self.is_running:
            print("❌ System is not running")
            return
        
        print("\n📊 Real-Time Email System Status")
        print("=" * 40)
        
        if self.monitor:
            status = self.monitor.get_status()
            print(f"📧 Email Monitoring: {'✅ Running' if status['is_running'] else '❌ Stopped'}")
            print(f"⏱️  Polling Interval: {status['polling_interval']} seconds")
            if status['last_check_time']:
                print(f"🕐 Last Check: {status['last_check_time']}")
        
        print(f"🤖 Telegram Bot: {'✅ Running' if self.bot_thread and self.bot_thread.is_alive() else '❌ Stopped'}")
        print(f"💾 Cache Files: {'✅ Persistent' if os.path.exists('telegram_email_cache.pkl') else '❌ None'}")

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    print("\n⛔ Received interrupt signal")
    sys.exit(0)

def main():
    """Main entry point."""
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check environment
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("❌ TELEGRAM_BOT_TOKEN not found in .env file")
        print("   Please set up your Telegram bot first")
        return
    
    if not os.getenv('TELEGRAM_CHAT_ID'):
        print("❌ TELEGRAM_CHAT_ID not found in .env file")
        print("   Run: python get_chat_id.py to get your chat ID")
        return
    
    # Create and start system
    system = RealTimeEmailSystem()
    
    try:
        system.start()
    except KeyboardInterrupt:
        print("\n⛔ Interrupted by user")
    finally:
        system.stop()
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()