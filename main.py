#!/usr/bin/env python3
"""
Smart Email Assistant - Main Entry Point
An AI-powered email assistant that categorizes emails, auto-drafts responses, and schedules meetings.
"""

import os
import sys
from dotenv import load_dotenv
from email_assistant.controller import EmailAssistantController
from email_assistant.dashboard import run_dashboard

def main():
    """Main entry point for the Smart Email Assistant."""
    load_dotenv()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--dashboard':
        print("Starting Streamlit dashboard...")
        run_dashboard()
    else:
        print("Starting Smart Email Assistant...")
        controller = EmailAssistantController()
        controller.run()

if __name__ == "__main__":
    main()