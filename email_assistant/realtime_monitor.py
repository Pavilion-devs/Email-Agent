"""Real-time email monitoring using Gmail API polling."""

import os
import time
import threading
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dotenv import load_dotenv
from .gmail_client import GmailClient
from .telegram_handler import TelegramEmailHandler
from .ollama_agents import OllamaEmailCategorizerAgent

class RealTimeEmailMonitor:
    """Monitor Gmail for new emails in real-time and process them immediately."""
    
    def __init__(self, polling_interval: int = 30):
        """Initialize the real-time monitor.
        
        Args:
            polling_interval: How often to check for new emails (seconds)
        """
        # Load environment variables
        load_dotenv()
        
        self.polling_interval = polling_interval
        self.gmail_client = None
        self.telegram_handler = None
        self.categorizer_agent = None
        self.is_running = False
        self.last_check_time = None
        self.monitoring_thread = None
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize Gmail client, Telegram handler, and AI agent."""
        try:
            self.gmail_client = GmailClient()
            print("✅ Gmail client initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Gmail client: {e}")
            return False
        
        try:
            self.telegram_handler = TelegramEmailHandler()
            print("✅ Telegram handler initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Telegram handler: {e}")
            return False
        
        try:
            self.categorizer_agent = OllamaEmailCategorizerAgent()
            print("✅ Ollama categorizer initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Ollama agent: {e}")
            return False
        
        return True
    
    def start_monitoring(self):
        """Start real-time email monitoring in a background thread."""
        if self.is_running:
            print("⚠️  Monitor is already running")
            return
        
        if not all([self.gmail_client, self.telegram_handler, self.categorizer_agent]):
            print("❌ Cannot start monitoring - components not initialized")
            return
        
        print("🚀 Starting real-time email monitoring...")
        print(f"📊 Polling interval: {self.polling_interval} seconds")
        
        self.is_running = True
        self.last_check_time = datetime.now() - timedelta(minutes=5)  # Check last 5 minutes initially
        
        # Start monitoring in background thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        print("✅ Real-time monitoring started!")
        print("   Press Ctrl+C to stop")
    
    def stop_monitoring(self):
        """Stop real-time email monitoring."""
        if not self.is_running:
            return
        
        print("\n⛔ Stopping real-time email monitoring...")
        self.is_running = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        print("✅ Real-time monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop that runs in background thread."""
        error_count = 0
        max_errors = 5
        
        while self.is_running:
            try:
                # Check for new emails
                new_emails = self._check_for_new_emails()
                
                if new_emails:
                    print(f"📧 Found {len(new_emails)} new email(s)")
                    self._process_new_emails(new_emails)
                else:
                    print(f"🔍 No new emails (checked at {datetime.now().strftime('%H:%M:%S')})")
                
                # Reset error count on successful check
                error_count = 0
                
                # Update last check time
                self.last_check_time = datetime.now()
                
                # Wait before next check
                time.sleep(self.polling_interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                error_count += 1
                print(f"❌ Error in monitoring loop ({error_count}/{max_errors}): {e}")
                
                if error_count >= max_errors:
                    print("❌ Too many errors, stopping monitoring")
                    break
                
                # Wait longer on error
                time.sleep(min(60, self.polling_interval * 2))
        
        self.is_running = False
    
    def _check_for_new_emails(self) -> List[Dict]:
        """Check Gmail for new emails since last check."""
        if not self.gmail_client or not self.last_check_time:
            return []
        
        try:
            # Get emails since last check
            since_time = self.last_check_time.strftime('%Y/%m/%d')
            query = f'in:inbox after:{since_time}'
            
            # Get recent messages
            messages = self.gmail_client.get_messages(query=query, max_results=10)
            
            # Filter to only emails newer than last check
            new_emails = []
            for message in messages:
                # Parse email date
                email_date = self._parse_email_date(message.get('date'))
                if email_date and email_date > self.last_check_time:
                    new_emails.append(message)
            
            return new_emails
            
        except Exception as e:
            print(f"❌ Error checking for new emails: {e}")
            return []
    
    def _parse_email_date(self, date_str: str) -> Optional[datetime]:
        """Parse email date string to datetime object."""
        if not date_str:
            return None
        
        try:
            # Try common date formats
            formats = [
                '%a, %d %b %Y %H:%M:%S %z',
                '%d %b %Y %H:%M:%S %z',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S'
            ]
            
            for fmt in formats:
                try:
                    # Remove timezone info for parsing if present
                    clean_date = date_str.split(' (')[0]  # Remove timezone names like "(UTC)"
                    return datetime.strptime(clean_date, fmt.replace(' %z', ''))
                except ValueError:
                    continue
            
            # If all parsing fails, return current time (will be processed)
            return datetime.now()
            
        except Exception:
            return None
    
    def _process_new_emails(self, new_emails: List[Dict]):
        """Process new emails with AI categorization and Telegram notifications."""
        try:
            # Categorize emails using Ollama
            categorized_emails = []
            
            for email in new_emails:
                try:
                    # Categorize with AI
                    category = self.categorizer_agent.categorize_email(email)
                    email['ai_category'] = category
                    
                    # Check if it's a meeting request
                    email['is_meeting_request'] = self._is_meeting_request(email)
                    
                    categorized_emails.append(email)
                    
                    print(f"   📂 Categorized: {email.get('subject', 'No Subject')[:40]}... → {category}")
                    
                except Exception as e:
                    print(f"❌ Error categorizing email: {e}")
                    # Add with default category
                    email['ai_category'] = 'Important'
                    email['is_meeting_request'] = False
                    categorized_emails.append(email)
            
            # Send notifications for important emails
            if categorized_emails:
                notification_count = self.telegram_handler.process_important_emails(categorized_emails)
                
                if notification_count > 0:
                    print(f"📱 Sent {notification_count} real-time notification(s)")
                else:
                    print("🔇 No notifications sent (emails filtered out)")
            
        except Exception as e:
            print(f"❌ Error processing new emails: {e}")
    
    def _is_meeting_request(self, email_data: Dict) -> bool:
        """Check if email is a meeting request."""
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', email_data.get('snippet', '')).lower()
        
        meeting_keywords = [
            'meeting', 'call', 'conference', 'zoom', 'teams', 'webinar',
            'appointment', 'schedule', 'calendar', 'invite', 'invitation'
        ]
        
        return any(keyword in subject or keyword in body for keyword in meeting_keywords)
    
    def get_status(self) -> Dict:
        """Get current monitoring status."""
        return {
            'is_running': self.is_running,
            'polling_interval': self.polling_interval,
            'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
            'components_initialized': all([self.gmail_client, self.telegram_handler, self.categorizer_agent])
        }
    
    def run_single_check(self):
        """Run a single check for new emails (for testing)."""
        if not all([self.gmail_client, self.telegram_handler, self.categorizer_agent]):
            print("❌ Components not initialized")
            return
        
        print("🔍 Running single email check...")
        self.last_check_time = datetime.now() - timedelta(minutes=10)
        
        new_emails = self._check_for_new_emails()
        if new_emails:
            print(f"📧 Found {len(new_emails)} email(s)")
            self._process_new_emails(new_emails)
        else:
            print("📭 No new emails found")

def main():
    """Main function for running real-time monitoring as standalone script."""
    print("🚀 Starting Real-Time Email Monitor")
    print("=" * 50)
    
    # Create monitor with 30-second polling
    monitor = RealTimeEmailMonitor(polling_interval=30)
    
    try:
        # Start monitoring
        monitor.start_monitoring()
        
        # Keep main thread alive
        while monitor.is_running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⛔ Received stop signal")
    finally:
        monitor.stop_monitoring()
        print("✅ Real-time monitor stopped")

if __name__ == "__main__":
    main()