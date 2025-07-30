# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Smart Email Assistant** - an AI-powered system that automatically categorizes emails, generates responses, and schedules meetings using Gmail API, Google Calendar API, and OpenAI's GPT-4 via LangChain.

## Key Commands

### Installation and Setup
```bash
pip install -r requirements.txt
python test_emails.py  # Test AI agents without Gmail API
```

### Running the Application
```bash
python main.py                    # Console mode
python main.py --dashboard        # Streamlit dashboard
streamlit run email_assistant/dashboard.py  # Direct dashboard launch
```

### Testing
```bash
python test_emails.py            # Test AI agents with sample emails
```

## Architecture Overview

### Core Components
- **EmailFetcher** (`email_fetcher.py`) - Gmail API wrapper for retrieving emails
- **GmailClient** (`gmail_client.py`) - Low-level Gmail operations (fetch, send, label)
- **CalendarClient** (`calendar_client.py`) - Google Calendar integration for meeting scheduling
- **EmailAssistantController** (`controller.py`) - Main orchestrator that coordinates all agents

### AI Agents (LangChain-based)
- **EmailCategorizerAgent** - Categorizes emails into: Important, Newsletters, Promotions, Meetings, Personal
- **EmailResponderAgent** - Generates contextual email responses using GPT-4
- **MeetingSchedulerAgent** - Detects meeting requests and extracts scheduling details

### User Interface
- **Dashboard** (`dashboard.py`) - Streamlit web interface for demo and visualization

## Configuration

### Environment Variables (.env)
- `OPENAI_API_KEY` - Required for GPT-4 access
- `GMAIL_CREDENTIALS_FILE` - OAuth credentials for Gmail API (default: credentials.json)
- `CALENDAR_CREDENTIALS_FILE` - OAuth credentials for Calendar API (default: calendar_credentials.json)
- `MAX_EMAILS` - Number of emails to process (default: 50)
- `AUTO_SEND` - Enable automatic email sending (default: false)
- `DEMO_MODE` - Show detailed console output (default: true)

### Required Files
- `credentials.json` - Gmail API OAuth credentials from Google Cloud Console
- `calendar_credentials.json` - Calendar API OAuth credentials
- `token.json` and `calendar_token.json` - Generated after first OAuth flow

## Development Workflow

1. **First-time setup**: Run authentication flow with `python main.py`
2. **Testing agents**: Use `python test_emails.py` to test AI functionality
3. **Development**: Modify agents in `agents.py` or add new components
4. **Demo**: Use dashboard mode for visual testing and presentations

## Key Features

- **Email Processing**: Fetches up to 50 recent emails via Gmail API
- **AI Categorization**: Uses GPT-4 to categorize emails with 90%+ accuracy
- **Response Generation**: Creates contextual replies for emails requiring responses
- **Meeting Detection**: Identifies scheduling requests and suggests available times
- **Gmail Integration**: Adds labels and sends responses via Gmail API
- **Calendar Integration**: Creates calendar events for scheduled meetings
- **Safety Mode**: Demo mode prevents accidental email sending

## Important Notes

- The system runs in demo mode by default (no emails sent automatically)
- All AI operations use OpenAI's GPT-4 via LangChain
- Gmail and Calendar APIs require OAuth authentication
- Project follows Google API rate limits and best practices
- Response generation respects email tone and context