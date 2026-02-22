# Setup Instructions

## 1. Gmail API Credentials

### Get Your Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Gmail API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Choose **Desktop App** as application type
6. Download the JSON file

### Setup
1. Rename the downloaded file to `credentials.json`
2. Place it in the `EmailClassifierAssistant/` directory
3. The file should match the structure in `credentials.json.example`

**IMPORTANT:** Never commit `credentials.json` to GitHub! It's already in `.gitignore`

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Run the Application

```bash
python server.py
```

On first run, it will:
- Open a browser for Gmail authentication
- Create a `token_[your-email].json` file (also protected by .gitignore)
- Start the server at http://127.0.0.1:8000

## 4. Multi-Account Support

To add more Gmail accounts:
1. Click the account avatar (top right)
2. Click "Add Account"
3. Authenticate with another Gmail account
4. Switch between accounts anytime

## Security Notes

Protected files (never committed to git):
- `credentials.json` - Your OAuth credentials
- `token_*.json` - Authentication tokens
- `__pycache__/` - Python cache

These are all listed in `.gitignore`
