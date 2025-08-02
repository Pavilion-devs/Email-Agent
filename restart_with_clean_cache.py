#!/usr/bin/env python3
"""Restart the email system with a clean cache to fix filtering issues."""

import os
import subprocess
import signal
import time
import sys

def stop_current_process():
    """Stop the currently running start_realtime.py process."""
    print("🛑 Stopping current email monitoring process...")
    
    try:
        # Find the process
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        for line in lines:
            if 'start_realtime.py' in line and 'grep' not in line:
                parts = line.split()
                if len(parts) > 1:
                    pid = parts[1]
                    print(f"   Found process PID: {pid}")
                    
                    # Kill the process
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"   Sent SIGTERM to PID {pid}")
                    
                    # Wait a moment
                    time.sleep(2)
                    
                    # Check if it's still running
                    try:
                        os.kill(int(pid), 0)  # Check if process exists
                        print(f"   Process still running, sending SIGKILL...")
                        os.kill(int(pid), signal.SIGKILL)
                    except OSError:
                        print(f"   Process stopped successfully")
                    
                    return True
        
        print("   No start_realtime.py process found")
        return False
        
    except Exception as e:
        print(f"   Error stopping process: {e}")
        return False

def clear_cache():
    """Clear the email cache files."""
    print("🧹 Clearing email cache...")
    
    cache_files = [
        'telegram_email_cache.pkl',
        'telegram_responses_cache.pkl'
    ]
    
    for cache_file in cache_files:
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                print(f"   ✅ Removed {cache_file}")
            except Exception as e:
                print(f"   ❌ Error removing {cache_file}: {e}")
        else:
            print(f"   ⚠️  {cache_file} not found")

def restart_system():
    """Restart the email monitoring system."""
    print("🚀 Restarting email monitoring system...")
    
    try:
        # Start the system in the background
        subprocess.Popen([sys.executable, 'start_realtime.py'], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
        
        print("   ✅ System restarted in background")
        print("   📱 Check your Telegram bot for new notifications")
        print("   🔍 Promotional emails should now be properly filtered")
        
    except Exception as e:
        print(f"   ❌ Error restarting system: {e}")

def main():
    """Main function to restart the system with clean cache."""
    print("🔄 RESTARTING EMAIL SYSTEM WITH CLEAN CACHE")
    print("=" * 50)
    
    # Step 1: Stop current process
    stop_current_process()
    
    # Step 2: Clear cache
    clear_cache()
    
    # Step 3: Restart system
    restart_system()
    
    print("\n✅ System restart complete!")
    print("\n📋 Next steps:")
    print("   1. Check your Telegram bot for the restart notification")
    print("   2. Send a test email to verify filtering is working")
    print("   3. Monitor that promotional emails are now blocked")

if __name__ == "__main__":
    main() 