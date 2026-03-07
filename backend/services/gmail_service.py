"""
Gmail API service for email fetching and management.
"""
import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from functools import wraps

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from backend.config import (
    GMAIL_SCOPES, CREDENTIALS_PATH, BASE_DIR,
    RATE_LIMIT_DELAY, MAX_RETRIES, INITIAL_BACKOFF
)


def rate_limited_api_call(func):
    """Decorator for rate limiting Gmail API calls."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        retries = 0
        backoff = INITIAL_BACKOFF
        
        while retries < MAX_RETRIES:
            try:
                time.sleep(RATE_LIMIT_DELAY)
                return func(*args, **kwargs)
            except HttpError as error:
                if error.resp.status in [429, 503]:
                    retries += 1
                    if retries >= MAX_RETRIES:
                        print(f"Max retries reached for {func.__name__}")
                        raise
                    
                    wait_time = backoff * (2 ** (retries - 1))
                    print(f"Rate limit hit. Waiting {wait_time}s before retry {retries}/{MAX_RETRIES}...")
                    time.sleep(wait_time)
                else:
                    raise
        return None
    return wrapper


class GmailService:
    """Service for Gmail API operations."""
    
    def __init__(self):
        """Initialize Gmail service."""
        self.base_dir = BASE_DIR
    
    def get_connected_accounts(self) -> List[str]:
        """Get list of connected Gmail accounts."""
        connected_accounts = []
        
        for file in os.listdir(self.base_dir):
            if file.startswith("token_") and file.endswith(".json"):
                acc_name = file[6:-5]
                if acc_name != "default":
                    connected_accounts.append(acc_name)
        
        if not connected_accounts and os.path.exists(self.base_dir / "token_default.json"):
            connected_accounts.append("default")
        
        return connected_accounts
    
    def create_auth_flow(self, redirect_uri: str) -> Tuple[str, str]:
        """
        Create OAuth flow and return authorization URL.
        
        Args:
            redirect_uri: OAuth callback URL
            
        Returns:
            Tuple of (authorization_url, state)
        """
        flow = Flow.from_client_secrets_file(
            str(CREDENTIALS_PATH),
            scopes=GMAIL_SCOPES,
            redirect_uri=redirect_uri
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return authorization_url, state
    
    def handle_auth_callback(self, code: str, backend_url: str) -> str:
        """
        Handle OAuth callback and save credentials.
        
        Args:
            code: Authorization code from Google
            backend_url: Backend URL for redirect URI
            
        Returns:
            Email address of authenticated user
        """
        redirect_uri = f"{backend_url}/api/auth/callback"
        
        flow = Flow.from_client_secrets_file(
            str(CREDENTIALS_PATH),
            scopes=GMAIL_SCOPES,
            redirect_uri=redirect_uri
        )
        
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        # Get user's email address
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        email_address = profile.get('emailAddress', 'default')
        
        # Save credentials
        token_path = self.base_dir / f'token_{email_address}.json'
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        
        return email_address
    
    def authenticate(self, account_id: str = "default"):
        """
        Authenticate with Gmail API.
        
        Args:
            account_id: Account identifier
            
        Returns:
            Gmail service object or None
        """
        token_path = self.base_dir / f'token_{account_id}.json'
        
        if not token_path.exists():
            return None
        
        creds = Credentials.from_authorized_user_file(str(token_path), GMAIL_SCOPES)
        
        # Refresh if expired
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Failed to refresh token: {e}")
                return None
        
        if not creds or not creds.valid:
            return None
        
        try:
            service = build('gmail', 'v1', credentials=creds)
            return service
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    
    @rate_limited_api_call
    def fetch_emails(self, service, max_results: int = 50, query: str = "in:inbox") -> List[Dict[str, Any]]:
        """
        Fetch emails from Gmail.
        
        Args:
            service: Gmail service object
            max_results: Maximum number of emails to fetch
            query: Gmail search query
            
        Returns:
            List of email dictionaries
        """
        try:
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            emails = []
            for msg in messages:
                email_data = self._get_email_details(service, msg['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    @rate_limited_api_call
    def _get_email_details(self, service, msg_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a single email."""
        try:
            message = service.users().messages().get(
                userId='me',
                id=msg_id,
                format='metadata',
                metadataHeaders=['From', 'Subject']
            ).execute()
            
            headers = message.get('payload', {}).get('headers', [])
            
            subject = ''
            sender = ''
            for header in headers:
                if header['name'] == 'Subject':
                    subject = header['value']
                elif header['name'] == 'From':
                    sender = header['value']
            
            snippet = message.get('snippet', '')
            
            return {
                'id': msg_id,
                'subject': subject,
                'sender': sender,
                'snippet': snippet
            }
        except HttpError as error:
            print(f'Error fetching email {msg_id}: {error}')
            return None
    
    @rate_limited_api_call
    def delete_messages(self, service, message_ids: List[str]) -> int:
        """Delete multiple messages."""
        count = 0
        for msg_id in message_ids:
            try:
                service.users().messages().delete(userId='me', id=msg_id).execute()
                count += 1
            except HttpError as error:
                print(f'Error deleting message {msg_id}: {error}')
        return count
    
    @rate_limited_api_call
    def archive_messages(self, service, message_ids: List[str]) -> int:
        """Archive multiple messages by removing INBOX label."""
        count = 0
        for msg_id in message_ids:
            try:
                service.users().messages().modify(
                    userId='me',
                    id=msg_id,
                    body={'removeLabelIds': ['INBOX']}
                ).execute()
                count += 1
            except HttpError as error:
                print(f'Error archiving message {msg_id}: {error}')
        return count
