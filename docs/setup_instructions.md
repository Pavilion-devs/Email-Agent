# Smart Email Assistant Setup Instructions

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Gmail account** with access to Google Cloud Console
3. **OpenAI API key** for GPT-4 access

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Gmail API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API and Google Calendar API
4. Create credentials (OAuth 2.0 Client ID) for a desktop application
5. Download the credentials file and save as `credentials.json` in the project root
6. For Calendar API, create separate credentials and save as `calendar_credentials.json`

### 3. Configure Environment Variables

1. Copy `.env.example` to `.env`
2. Add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### 4. First Run (Authentication)

```bash
python main.py
```

This will:
- Open a browser for Gmail OAuth authentication
- Generate `token.json` and `calendar_token.json` files
- Process your emails for the first time

### 5. Run the Dashboard

```bash
python main.py --dashboard
```

Or with Streamlit directly:
```bash
streamlit run email_assistant/dashboard.py
```

## Configuration Options

Edit the `.env` file to customize:

- `MAX_EMAILS`: Number of emails to process (default: 50)
- `EMAIL_CATEGORIES`: Comma-separated list of categories
- `DEMO_MODE`: Enable detailed console output (default: true)
- `AUTO_SEND`: Automatically send responses (default: false)

## Demo Mode

The assistant runs in demo mode by default, which:
- Shows detailed processing information
- Does not automatically send emails
- Provides preview of all AI-generated content

To enable automatic actions, set `AUTO_SEND=true` in your `.env` file.

## Troubleshooting

### Common Issues

1. **"Credentials file not found"**
   - Make sure you've downloaded and renamed the credentials files correctly

2. **"OpenAI API key not found"**
   - Check your `.env` file and ensure the API key is set

3. **"Permission denied" for Gmail**
   - Re-run the authentication flow and grant all requested permissions

4. **Import errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

### Getting Help

- Check the console output for detailed error messages
- Ensure your Gmail account has API access enabled
- Verify your OpenAI API key has sufficient credits

## Features

- ✅ Email categorization (Important, Newsletters, Promotions, Meetings, Personal)
- ✅ Automatic response generation
- ✅ Meeting request detection and scheduling
- ✅ Gmail label management
- ✅ Interactive dashboard
- ✅ Demo mode for safe testing