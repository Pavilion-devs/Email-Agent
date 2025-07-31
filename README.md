# 🤖 Smart Email Assistant

A powerful AI-powered email automation system that processes your Gmail in real-time, categorizes emails with local AI, and sends smart notifications to Telegram with interactive response capabilities.

## ✨ Features

### 🚀 **Real-Time Email Processing**
- **Instant monitoring** - Checks Gmail every 30 seconds for new emails
- **Immediate notifications** - Get alerted within seconds of receiving important emails
- **Background processing** - Runs continuously without interrupting your workflow

### 🧠 **100% Free Local AI Processing**
- **Ollama integration** - Uses local `llama3.2:3b` model (completely free)
- **Smart categorization** - Automatically sorts emails into Important, Meetings, Personal, Newsletters, Promotions
- **Intelligent filtering** - Only sends notifications for emails that matter

### 📱 **Smart Telegram Notifications**
- **Selective notifications** - Only for Important emails, Meeting requests, and Personal messages
- **Interactive buttons** - Reply, Schedule, View Full, Mark Done directly from Telegram
- **AI-generated responses** - Get suggested replies powered by local AI
- **Meeting scheduling** - Automatic calendar integration for meeting requests

### 🔒 **Privacy & Security**
- **Local AI processing** - No data sent to external AI services
- **Secure OAuth** - Uses Google's official authentication
- **Persistent cache** - Email data saved locally for reliable button interactions

## 🛠️ Prerequisites

Before setting up the Smart Email Assistant, ensure you have:

- **Python 3.8+** installed on your system
- **Gmail account** with API access
- **Telegram account** for notifications
- **Ollama** installed with llama3.2:3b model

## 📋 Quick Setup Guide

### 1. **Install Ollama (Local AI)**

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows - Download from https://ollama.ai/download
```

**Download the AI model:**
```bash
ollama pull llama3.2:3b
```

### 2. **Clone and Setup Project**

```bash
# Clone or download the project
cd /path/to/smart-email-assistant

# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. **Google Cloud Console Setup**

1. **Go to** [Google Cloud Console](https://console.cloud.google.com/)
2. **Create a new project** or select existing one
3. **Enable APIs:**
   - Gmail API
   - Google Calendar API
4. **Create credentials:**
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
   - Application type: **Desktop application**
   - Download the JSON file as `credentials.json`
5. **Place the file** in the project root directory

### 4. **Telegram Bot Setup**

1. **Create a bot:**
   - Open Telegram and search for `@BotFather`
   - Send `/newbot`
   - Choose name: `Smart Email Assistant`
   - Choose username: `your_email_assistant_bot`
   - Copy the bot token

2. **Get your Chat ID:**
   ```bash
   python3 get_chat_id.py
   ```
   - Follow the instructions to get your chat ID

### 5. **Environment Configuration**

Create a `.env` file in the project root:

```bash
# Copy example configuration
cp .env.example .env
```

**Edit `.env` file:**
```env
# Google API Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Gmail API Configuration
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json

# Google Calendar API Configuration
CALENDAR_CREDENTIALS_FILE=calendar_credentials.json
CALENDAR_TOKEN_FILE=calendar_token.json

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Email Configuration
MAX_EMAILS=50
EMAIL_CATEGORIES=Important,Newsletters,Promotions,Meetings,Personal

# Demo Configuration
DEMO_MODE=false
AUTO_SEND=false

# Ollama Configuration (Local AI)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

## 🚀 Usage

### **Real-Time Email System (Recommended)**

Start the complete real-time system:

```bash
python3 start_realtime.py
```

This will:
- ✅ Monitor Gmail in real-time (30-second intervals)
- ✅ Process emails with local AI
- ✅ Send smart Telegram notifications
- ✅ Handle interactive button responses
- ✅ Provide meeting scheduling capabilities

### **Manual Email Processing**

Process emails once:

```bash
python3 main.py
```

### **Telegram Bot Server Only**

Run just the Telegram bot for handling callbacks:

```bash
python3 telegram_bot_server.py
```

## 📊 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Gmail API     │◄──►│  Smart Email     │◄──►│  Telegram Bot   │
│                 │    │   Assistant      │    │                 │
│ • Email Fetch   │    │                  │    │ • Notifications │
│ • Send Replies  │    │ • AI Processing  │    │ • Interactive   │
│ • Authentication│    │ • Categorization │    │   Buttons       │
└─────────────────┘    │ • Real-time Mon. │    │ • Response Gen. │
                       └──────────────────┘    └─────────────────┘
                              │
                       ┌──────────────────┐
                       │   Local Ollama   │
                       │                  │
                       │ • llama3.2:3b    │
                       │ • 100% Free      │
                       │ • Privacy Safe   │
                       └──────────────────┘
```

## 📱 Smart Filtering Logic

The system intelligently filters emails to prevent notification spam:

### ✅ **Will Notify:**
- **Important emails** - Account security, deadlines, urgent matters
- **Meeting requests** - Calendar invitations, scheduling emails
- **Personal emails** - Direct communications that could be business opportunities

### ❌ **Will NOT Notify:**
- **Newsletters** - Marketing emails, subscription updates
- **Promotions** - Sales, discounts, shopping offers
- **Spam/Low Priority** - Automated notifications, social media alerts

## 🎯 Interactive Features

### **Telegram Bot Commands:**
- `/start` - Show welcome message and setup info
- `/status` - Check system status
- `/test` - Send test notification

### **Interactive Buttons:**
- **✍️ Reply** - Generate AI-powered response
- **📅 Schedule** - Create calendar meeting
- **👀 View Full** - See complete email content
- **✅ Mark Done** - Archive and dismiss
- **🔇 Ignore** - Dismiss without action

## 🔧 Troubleshooting

### **Common Issues:**

1. **"TELEGRAM_BOT_TOKEN not found"**
   ```bash
   # Check your .env file has the correct token
   cat .env | grep TELEGRAM_BOT_TOKEN
   ```

2. **"Gmail client not available"**
   ```bash
   # Re-authenticate with Gmail
   rm token.json
   python3 main.py
   ```

3. **"Ollama connection failed"**
   ```bash
   # Check Ollama is running
   ollama serve
   ollama run llama3.2:3b
   ```

4. **"Button callbacks not working"**
   ```bash
   # Check for cache files
   ls -la telegram_email_cache.pkl
   # Restart the real-time system
   python3 start_realtime.py
   ```

### **Logs and Debugging:**

The system provides detailed logging:
- ✅ Gmail authentication status
- 📧 Email processing results  
- 🤖 AI categorization decisions
- 📱 Telegram notification delivery
- 🔍 Real-time monitoring activity

## ⚙️ Configuration Options

### **Polling Interval:**
Modify `polling_interval` in `start_realtime.py`:
```python
monitor = RealTimeEmailMonitor(polling_interval=60)  # Check every 60 seconds
```

### **Email Categories:**
Update categories in `.env`:
```env
EMAIL_CATEGORIES=Important,Newsletters,Promotions,Meetings,Personal,Work
```

### **Notification Priority:**
Customize priority levels in `telegram_bot.py`:
```python
def get_notification_priority(self, email_data: Dict) -> str:
    # Add your custom priority logic
```

## 📁 Project Structure

```
smart-email-assistant/
├── 📁 email_assistant/          # Core application modules
│   ├── gmail_client.py          # Gmail API wrapper
│   ├── telegram_bot.py          # Telegram bot integration
│   ├── telegram_handler.py      # Callback handling
│   ├── ollama_agents.py         # Local AI agents
│   ├── realtime_monitor.py      # Real-time email monitoring
│   ├── calendar_client.py       # Google Calendar integration
│   └── controller.py            # Main controller
├── 📁 tests/                    # Test files
│   ├── test_telegram.py         # Telegram bot tests
│   ├── test_ollama.py           # AI agent tests
│   └── observation.txt          # Test results
├── 📁 docs/                     # Documentation
│   ├── prd.txt                  # Product requirements
│   └── setup_instructions.md    # Setup guide
├── start_realtime.py            # 🚀 Main real-time launcher
├── main.py                      # Manual email processing
├── get_chat_id.py               # Telegram setup helper
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
└── README.md                    # This file
```

## 🔐 Security & Privacy

- **Local AI Processing** - All email analysis happens on your machine
- **No Data Leakage** - Emails never sent to external AI services
- **OAuth Security** - Uses Google's secure authentication
- **Token Management** - Automatic token refresh and secure storage
- **Cache Encryption** - Email cache files stored locally

## 📈 Performance & Limits

### **Gmail API Quotas:**
- **Daily Limit:** 1 billion quota units (very generous)
- **Per User:** 250 quota units per 100 seconds  
- **Current Usage:** ~29K units/day (0.003% of limit)
- **Safety Rating:** 🟢 Very Safe

### **System Requirements:**
- **RAM:** 2GB minimum (4GB recommended for Ollama)
- **Storage:** 2GB for Ollama model + logs
- **Network:** Stable internet for Gmail/Telegram APIs

## 🆘 Support & Contributing

### **Getting Help:**
1. Check the troubleshooting section above
2. Review logs for error messages
3. Test individual components with test files
4. Ensure all prerequisites are installed

### **Feature Requests:**
Feel free to extend the system:
- Add new AI models
- Implement custom filters  
- Create additional notification channels
- Build web dashboard interface

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Ollama** - For providing free local AI capabilities
- **Google APIs** - For Gmail and Calendar integration  
- **Telegram Bot API** - For interactive notifications
- **LangChain** - For AI agent orchestration

---

### 🎉 **Ready to Transform Your Email Experience?**

Run the setup steps above and execute:

```bash
python3 start_realtime.py
```

Your intelligent email assistant will start monitoring your inbox and sending smart notifications to Telegram! 🚀

**Never miss an important email again while staying free from notification spam!** ✨