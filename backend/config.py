"""
Configuration management for the email classifier backend.
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# Gmail API Configuration
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_PATH = BASE_DIR / "credentials.json"

# Rate Limiting
RATE_LIMIT_DELAY = 0.2  # seconds between API calls
MAX_RETRIES = 5
INITIAL_BACKOFF = 1.5  # seconds

# Classification Configuration
CATEGORIES = [
    'Important',
    'Transactional',
    'Promotional',
    'Social',
    'Spam'
]

# Category descriptions for intent-based classification
CATEGORY_DESCRIPTIONS = {
    'Important': 'Emails requiring immediate attention (job offers, interviews, account alerts, project updates)',
    'Transactional': 'Receipts, bank statements, order confirmations, delivery updates',
    'Promotional': 'Marketing emails, sales, advertisements, offers',
    'Social': 'LinkedIn invites, comments, social notifications',
    'Spam': 'Lottery scams, phishing, suspicious offers'
}

# Suggested actions per category
CATEGORY_ACTIONS = {
    'Important': 'Keep',
    'Transactional': 'Keep',
    'Promotional': 'Archive',
    'Social': 'Archive',
    'Spam': 'Delete'
}

# Model Configuration
TFIDF_MODEL_PATH = MODELS_DIR / "tfidf_classifier.pkl"
ZERO_SHOT_MODEL = "valhalla/distilbart-mnli-12-3"  # Lightweight model
USE_ZERO_SHOT = os.getenv("USE_ZERO_SHOT", "false").lower() == "true"  # Disabled by default

# Cache Configuration
CACHE_MAX_SIZE = 1000  # Maximum number of cached predictions
CACHE_TTL = 3600  # Cache time-to-live in seconds

# Memory Optimization
LAZY_LOAD_MODELS = True  # Load models only when needed
UNLOAD_UNUSED_MODELS = True  # Unload models after use to save memory

# Database
DB_PATH = DATA_DIR / "email_analytics.db"
FEEDBACK_CSV_PATH = DATA_DIR / "feedback_dataset.csv"

# Self-Learning Configuration
SELF_LEARNING_ENABLED = True  # Enable automatic retraining
FEEDBACK_RETRAIN_THRESHOLD = 50  # Retrain after N feedback samples
MIN_FEEDBACK_FOR_RETRAIN = 10  # Minimum feedback samples needed

# Server Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
PORT = int(os.getenv("PORT", 8000))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
