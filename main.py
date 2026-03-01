import os.path
import time
import pickle
from pathlib import Path
from functools import wraps

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

_ml_pipeline = None
_sentiment_pipeline = None
_tfidf_classifier = None
_classification_cache = {}

# Rate limiting configuration
RATE_LIMIT_DELAY = 0.5  # 500ms delay between API calls (very conservative)
MAX_RETRIES = 5
INITIAL_BACKOFF = 3  # seconds (increased from 2)

def rate_limited_api_call(func):
    """Decorator to add rate limiting and exponential backoff to Gmail API calls."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        retries = 0
        backoff = INITIAL_BACKOFF
        
        while retries < MAX_RETRIES:
            try:
                # Add small delay between calls
                time.sleep(RATE_LIMIT_DELAY)
                return func(*args, **kwargs)
            except HttpError as error:
                if error.resp.status in [429, 503]:  # Rate limit or service unavailable
                    retries += 1
                    if retries >= MAX_RETRIES:
                        print(f"Max retries reached for {func.__name__}")
                        raise
                    
                    wait_time = backoff * (2 ** (retries - 1))  # Exponential backoff
                    print(f"Rate limit hit. Waiting {wait_time}s before retry {retries}/{MAX_RETRIES}...")
                    time.sleep(wait_time)
                else:
                    raise
        
        return None
    return wrapper

def get_ml_classifier():
    """Lazily load the HuggingFace zero-shot classification pipeline."""
    global _ml_pipeline
    if _ml_pipeline is None:
        try:
            import numpy as np
            print(f"Numpy version: {np.__version__}")
            from transformers import pipeline
            print("Loading ML Classification Model (Valhalla DistilBART MNLI)...")
            # Using Valhalla's optimized distilbart-mnli model (smaller, faster)
            _ml_pipeline = pipeline(
                "zero-shot-classification", 
                model="valhalla/distilbart-mnli-12-3",  # Professor's recommendation
                device=-1,
                batch_size=8  # Process multiple emails at once
            )
            print("ML Classification Model loaded successfully.")
        except ImportError as e:
            print(f"Failed to import required libraries: {e}")
            import traceback
            traceback.print_exc()
            return None
        except Exception as e:
            print(f"Failed to load ML pipeline: {e}")
            import traceback
            traceback.print_exc()
            return None
    return _ml_pipeline

def get_sentiment_analyzer():
    """Lazily load the sentiment analysis pipeline."""
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        try:
            from transformers import pipeline
            print("Loading Sentiment Analysis Model (DistilBERT)...")
            _sentiment_pipeline = pipeline(
                "sentiment-analysis", 
                model="distilbert-base-uncased-finetuned-sst-2-english", 
                device=-1,
                batch_size=8
            )
            print("Sentiment Analysis Model loaded successfully.")
        except Exception as e:
            print(f"Failed to load sentiment pipeline: {e}")
            return None
    return _sentiment_pipeline


def get_tfidf_classifier():
    """
    Lazily load or train the TF-IDF + Logistic Regression classifier.
    This is a CPU-friendly alternative to zero-shot learning.
    Professor's recommendation: Better accuracy, faster inference.
    """
    global _tfidf_classifier
    if _tfidf_classifier is None:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
            from sklearn.pipeline import Pipeline
            import numpy as np
            
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(BASE_DIR, 'tfidf_model.pkl')
            
            # Try to load existing model
            if os.path.exists(model_path):
                print("Loading TF-IDF classifier from disk...")
                with open(model_path, 'rb') as f:
                    _tfidf_classifier = pickle.load(f)
                print("TF-IDF classifier loaded successfully.")
            else:
                print("Training new TF-IDF classifier...")
                # Train on synthetic data (will be replaced with real data after first scan)
                _tfidf_classifier = train_tfidf_classifier()
                
                # Save the model
                with open(model_path, 'wb') as f:
                    pickle.dump(_tfidf_classifier, f)
                print("TF-IDF classifier trained and saved.")
                
        except Exception as e:
            print(f"Failed to load/train TF-IDF classifier: {e}")
            import traceback
            traceback.print_exc()
            return None
    return _tfidf_classifier


def train_tfidf_classifier():
    """
    Train a TF-IDF + Logistic Regression classifier.
    Uses historical data from database if available, otherwise uses synthetic training data.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    
    # Try to get historical data from database
    try:
        from database import DB_PATH
        import sqlite3
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT subject, sender, category 
            FROM classifications 
            WHERE confidence > 0.7
            LIMIT 1000
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) > 50:  # Need at least 50 samples
            print(f"Training on {len(rows)} historical classifications...")
            texts = [f"{row[0]} {row[1]}" for row in rows]
            labels = [row[2] for row in rows]
        else:
            raise ValueError("Not enough historical data")
            
    except Exception as e:
        print(f"Using augmented training data: {e}")
        # Augmented training data for 5 categories (200+ examples)
        texts = [
            # Banking/Financial (40 examples)
            "Account statement for January 2024", "Your credit card payment is due tomorrow",
            "Transaction alert: Rs 5000 debited from your account", "Netbanking password reset successful",
            "UPI payment of Rs 2500 received", "Minimum balance alert in savings account",
            "Your loan EMI is due on 15th", "Credit card bill generated for this month",
            "NEFT transfer successful - Rs 10000", "IMPS transaction completed",
            "Account balance: Rs 45000 as of today", "Debit card blocked due to suspicious activity",
            "Fixed deposit matured - Rs 100000", "Interest credited to your account",
            "Overdraft facility activated", "Cheque bounce notification",
            "Standing instruction set up successfully", "Auto-debit enabled for bill payment",
            "Your account has been debited with Rs 1500", "Monthly account statement attached",
            "KYC update required for your bank account", "New credit card dispatched",
            "ATM withdrawal of Rs 3000", "Online banking registration successful",
            "Reward points credited - 500 points", "Credit limit increased to Rs 200000",
            "Payment reminder for credit card dues", "Account upgrade to premium tier",
            "Tax deducted at source - Rs 5000", "Mutual fund investment confirmation",
            "Insurance premium payment successful", "Loan application approved",
            "Direct deposit received from employer", "Wire transfer initiated",
            "Savings account interest rate changed", "Mobile banking app login detected",
            "Security alert: New device login", "Card CVV changed successfully",
            "Recurring deposit installment due", "Investment portfolio summary",
            "Forex transaction completed", "Cashback credited to account",
            
            # Shopping/Orders (40 examples)
            "Your Amazon order has been shipped", "Order confirmation - Order #12345",
            "Delivery scheduled for tomorrow between 10 AM - 2 PM", "Invoice for your recent purchase",
            "Package out for delivery", "Thank you for your order from Flipkart",
            "Your order has been delivered", "Return request approved",
            "Refund initiated for cancelled order", "Product review request",
            "Order dispatched from warehouse", "Tracking number: 1234567890",
            "Your Myntra order is arriving today", "Payment successful for order",
            "Order placed successfully", "Estimated delivery: 3-5 business days",
            "Your Swiggy order is being prepared", "Zomato: Your food is on the way",
            "Uber ride receipt", "Ola cab booking confirmed",
            "Your grocery order from BigBasket", "Blinkit: Order delivered",
            "Dunzo delivery completed", "Zepto order arriving in 10 minutes",
            "Your medicine order from PharmEasy", "1mg: Prescription uploaded successfully",
            "Lenskart: Your eyewear order shipped", "Nykaa order confirmation",
            "Ajio: Your fashion order dispatched", "Meesho order placed",
            "Your book order from Amazon", "Kindle purchase receipt",
            "Netflix subscription renewed", "Spotify premium payment",
            "Your flight ticket booking confirmed", "Hotel reservation successful",
            "Train ticket booked - PNR: 1234567890", "Bus ticket confirmation",
            "Movie ticket booking confirmed", "Event pass purchased",
            
            # Work/Career (40 examples)
            "Meeting scheduled for 3 PM today", "Job application received for Software Engineer",
            "Interview invitation for tomorrow", "Project deadline reminder - Due Friday",
            "LinkedIn connection request from John Doe", "Your resume has been shortlisted",
            "Naukri: New job alert matching your profile", "Indeed: 5 new jobs for you",
            "Glassdoor: Company review request", "AngelList: Startup job opportunity",
            "Internshala: Internship application update", "Unstop: Hackathon registration confirmed",
            "Team meeting rescheduled to 4 PM", "Conference call link for client meeting",
            "Slack: You were mentioned in #general", "Microsoft Teams meeting invite",
            "Zoom meeting starting in 10 minutes", "Google Meet link for interview",
            "Your timesheet is pending approval", "Leave application approved",
            "Salary slip for January 2024", "Offer letter from XYZ Company",
            "Background verification initiated", "Onboarding documents required",
            "Performance review scheduled", "Training session tomorrow at 11 AM",
            "Project update from manager", "Code review requested on GitHub",
            "Pull request merged successfully", "Build failed - Action required",
            "Jira: New task assigned to you", "Trello: Card moved to In Progress",
            "Asana: Project deadline approaching", "Monday.com: Status update needed",
            "Your article published on Medium", "LinkedIn: Your post got 100 likes",
            "GitHub: New follower", "Stack Overflow: Answer accepted",
            "Coursera: Course completion certificate", "Udemy: New course recommendation",
            
            # Promotional (40 examples)
            "50% off sale ends tonight - Shop now", "Limited time offer: Buy 1 Get 1 Free",
            "Exclusive deal just for you", "Flash sale starting in 1 hour",
            "Clearance sale: Up to 70% off", "Mega sale this weekend",
            "Don't miss: Biggest sale of the year", "Last chance to save big",
            "Special offer: Free shipping on all orders", "Discount code inside: SAVE20",
            "Subscribe now and get 3 months free", "Register today for early access",
            "Join our loyalty program", "Refer a friend and earn rewards",
            "Hot deal alert: Limited stock", "Price drop notification",
            "Your wishlist items are on sale", "Abandoned cart: Complete your purchase",
            "New arrivals: Check out latest collection", "Seasonal sale now live",
            "Black Friday deals starting now", "Cyber Monday exclusive offers",
            "Diwali special: Festive discounts", "Christmas sale: Gift ideas inside",
            "New Year offers: Start fresh", "Valentine's Day special deals",
            "Summer sale: Beat the heat", "Monsoon offers: Stay dry",
            "Back to school sale", "End of season clearance",
            "Member exclusive: Early access sale", "VIP sale: Invitation only",
            "Free trial for 30 days", "Upgrade now and save 40%",
            "Limited edition product launch", "Pre-order now: Special price",
            "Restock alert: Popular item back", "Price match guarantee",
            "Bundle offer: Save more", "Combo deal: Best value",
            
            # Personal/Other (40 examples)
            "Weekly newsletter from TechCrunch", "Your daily digest from Medium",
            "Monthly update from our community", "Facebook: Friend request from Jane",
            "Instagram: New follower", "Twitter: You were mentioned in a tweet",
            "WhatsApp: New message from Mom", "Telegram: New channel post",
            "Reddit: Your post got 50 upvotes", "Quora: New answer to your question",
            "Pinterest: New pin from your board", "Tumblr: New follower",
            "YouTube: New video from subscribed channel", "Spotify: New playlist for you",
            "Apple Music: Weekly mix ready", "Netflix: New shows added",
            "Prime Video: Watch list update", "Disney+: New episode released",
            "Webinar invitation: Learn about AI", "Online course enrollment confirmation",
            "Workshop registration successful", "Seminar reminder for tomorrow",
            "Podcast episode: New release", "Blog post: Weekly roundup",
            "News alert: Breaking news", "Weather update: Rain expected",
            "Sports update: Match highlights", "Horoscope for today",
            "Recipe of the day", "Fitness tip: Daily workout",
            "Meditation reminder", "Health tip: Stay hydrated",
            "Book recommendation: Bestseller", "Movie review: Latest release",
            "Travel guide: Top destinations", "Photography tips: Lighting basics",
            "Cooking class invitation", "Art exhibition this weekend",
            "Music concert tickets available", "Theater show booking open",
        ]
        
        labels = (
            ["Banking/Financial"] * 40 +
            ["Shopping/Orders"] * 40 +
            ["Work/Career"] * 40 +
            ["Promotional"] * 40 +
            ["Personal/Other"] * 40
        )
    
    # Create pipeline with improved hyperparameters for better accuracy
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=3000,        # Increased from 1000 for richer features
            ngram_range=(1, 3),       # Added trigrams for better phrase matching
            stop_words='english',
            min_df=1,
            max_df=0.95,              # Ignore very common terms
            sublinear_tf=True,        # Better handling of varying email lengths
            strip_accents='unicode'   # Handle special characters properly
        )),
        ('clf', LogisticRegression(
            max_iter=2000,              # Increased iterations for convergence
            multi_class='multinomial',
            solver='lbfgs',
            C=1.5,                      # Slightly less regularization
            class_weight='balanced',    # Handle imbalanced categories better
            random_state=42             # Reproducibility
        ))
    ])
    
    # Train
    pipeline.fit(texts, labels)
    return pipeline


def retrain_tfidf_from_database():
    """
    Retrain the TF-IDF classifier using historical data from the database.
    Call this periodically to improve accuracy.
    """
    global _tfidf_classifier
    
    try:
        print("Retraining TF-IDF classifier from database...")
        _tfidf_classifier = train_tfidf_classifier()
        
        # Save the updated model
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(BASE_DIR, 'tfidf_model.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(_tfidf_classifier, f)
        
        print("TF-IDF classifier retrained successfully.")
        return True
    except Exception as e:
        print(f"Failed to retrain TF-IDF classifier: {e}")
        return False


def classify_with_tfidf(subject, sender, body_snippet):
    """
    Classify email using TF-IDF + Logistic Regression.
    CPU-friendly alternative to zero-shot learning.
    Returns (category, confidence, all_scores).
    """
    classifier = get_tfidf_classifier()
    if not classifier:
        return "Other", 0.5, {}
    
    try:
        # Prepare text
        text = f"{subject} {sender} {body_snippet[:200]}"
        
        # Predict
        category = classifier.predict([text])[0]
        probabilities = classifier.predict_proba([text])[0]
        
        # Get all scores
        classes = classifier.classes_
        all_scores = {cls: float(prob) for cls, prob in zip(classes, probabilities)}
        
        # Get confidence for predicted category
        confidence = max(probabilities)
        
        return category, confidence, all_scores
        
    except Exception as e:
        print(f"TF-IDF classification error: {e}")
        return "Other", 0.5, {}

# If modifying these scopes, delete the token files to re-authenticate.
# We need full Gmail access to label, modify, and delete emails.
# Note: After changing scopes, you must delete token_*.json files and re-authenticate
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Alternative: Use full Gmail scope for deletion support
# SCOPES = ['https://mail.google.com/']

def authenticate_gmail(account_id="default"):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # Define absolute paths based on where main.py is located
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(BASE_DIR, f'token_{account_id}.json')
    creds_path = os.path.join(BASE_DIR, 'credentials.json')
    
    # The file token_{account_id}.json stores the user's access and refresh tokens
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        
        # If no explicit account_id was passed, let's grab the actual email address
        # and rename the token file to match their email for better tracking in the future.
        if account_id == "default":
            profile = service.users().getProfile(userId='me').execute()
            real_email = profile.get('emailAddress')
            if real_email:
                new_token_path = os.path.join(BASE_DIR, f"token_{real_email}.json")
                if token_path != new_token_path and not os.path.exists(new_token_path):
                    import shutil
                    shutil.move(token_path, new_token_path)
                    
        print(f"Successfully connected to the Gmail server for account: {account_id}!")
        return service
    except HttpError as error:
        print(f'An error occurred connecting to Gmail: {error}')
        return None

def extract_email_features(subject, sender, body_snippet):
    """
    Enterprise-level feature engineering for email classification.
    Extracts meaningful features that improve ML model performance.
    """
    features = {
        'subject_length': len(subject),
        'body_length': len(body_snippet),
        'has_numbers': any(char.isdigit() for char in subject + body_snippet),
        'has_currency': any(symbol in subject + body_snippet for symbol in ['$', '€', '£', '₹', 'Rs']),
        'has_percentage': '%' in subject + body_snippet,
        'has_urgency': any(word in (subject + body_snippet).lower() for word in ['urgent', 'asap', 'immediately', 'now']),
        'sender_domain': sender.split('@')[-1].split('>')[0].strip() if '@' in sender else 'unknown',
        'all_caps_ratio': sum(1 for c in subject if c.isupper()) / max(len(subject), 1),
        'exclamation_count': (subject + body_snippet).count('!'),
        'question_count': (subject + body_snippet).count('?')
    }
    return features


def classify_with_keywords(subject, sender, body_snippet, features):
    """
    Rule-based classification using keyword matching - UPDATED TO 5 CATEGORIES.
    Returns (category, confidence, matched_keywords) or (None, 0, []) if no match.
    STRENGTHENED: More keywords, better domain matching, higher confidence.
    """
    combined_text = f"{subject} {body_snippet}".lower()
    sender_lower = sender.lower()
    sender_domain = features['sender_domain'].lower()
    
    # Expanded keyword sets - CONSOLIDATED TO 5 CATEGORIES
    banking_keywords = [
        'account statement', 'transaction', 'balance', 'credit card', 'debit card',
        'payment', 'netbanking', 'upi', 'neft', 'rtgs', 'imps',
        'account alert', 'credited', 'debited', 'withdrawal', 'deposit',
        'statement for', 'minimum balance', 'overdraft', 'loan', 'emi', 'interest',
        'bank account', 'savings account', 'current account', 'fixed deposit',
        'mutual fund', 'investment', 'cheque', 'atm', 'card blocked', 'otp'
    ]
    banking_domains = ['bank', 'sbi', 'hdfc', 'icici', 'axis', 'kotak', 'paytm', 'phonepe', 'gpay', 'citi', 'hsbc', 'pnb', 'canara', 'idbi']
    
    shopping_keywords = [
        'order confirmation', 'receipt', 'invoice', 'shipped', 'delivery',
        'tracking', 'your order', 'purchase', 'payment successful', 'order placed',
        'dispatched', 'out for delivery', 'delivered', 'order #', 'order number',
        'thank you for your order', 'shipment', 'package', 'courier', 'tracking number',
        'order has been', 'order status', 'order update', 'estimated delivery'
    ]
    shopping_domains = ['amazon', 'flipkart', 'myntra', 'swiggy', 'zomato', 'uber', 'ola', 'ebay', 'shopify', 'meesho', 'ajio', 'nykaa']
    
    work_keywords = [
        'meeting scheduled', 'interview invitation', 'job application', 'resume shortlisted',
        'position available', 'hiring for', 'recruitment process', 'linkedin connection',
        'project deadline', 'task assigned', 'team meeting', 'colleague request',
        'conference call', 'job alert', 'job opening', 'candidate profile'
    ]
    work_domains = ['linkedin', 'naukri', 'indeed', 'glassdoor', 'angellist', 'internshala']
    
    # Personal/Other domains (newsletters, social, content platforms, education)
    personal_domains = ['soundcloud', 'spotify', 'youtube', 'perplexity', 'adobe', 'medium', 
                       'substack', 'honeygain', 'facebook', 'twitter', 'instagram',
                       'coursera', 'udemy', 'edx', 'claude', 'canva', 'notion', 'figma']
    
    # PRIORITY: Check promotional keywords FIRST
    promo_keywords = [
        'special offer', 'discount', 'sale ends', 'limited time', 'offer expires',
        'buy now', 'shop now', 'deal of', 'save up to', 'free trial', 'subscribe now',
        'exclusive offer', 'promotional', 'advertisement', '% off', 'claim your',
        'dont miss', "don't miss", 'last chance', 'hurry up', 'act now', 'limited offer',
        'flash sale', 'clearance sale', 'mega sale', 'biggest sale', 'promo code',
        'limited stock', 'while supplies last', 'today only', 'ends soon', 'ends today',
        'black friday', 'cyber monday', 'thanksgiving sale', 'holiday sale',
        'bonus offer', 'welcome back bonus', 'cashback offer', 'gift card',
        'congratulations you', "you've won", 'claim now', 'redeem now'
    ]
    
    # Personal/Other includes: newsletters, social, personal emails, education
    personal_keywords = [
        'newsletter from', 'weekly digest', 'monthly update', 'whats new in', "what's new in",
        'new feature', 'product update', 'introducing our', 'update from',
        'learn from', 'learn about', 'educational content', 'online course',
        'happy holidays', 'season greetings', 'thank you for', 'community update'
    ]
    
    matched_keywords = []
    
    # STEP 0: Check for personal/content platform domains FIRST
    # (SoundCloud, Adobe, Perplexity, etc. should be Personal, not promotional)
    has_personal_domain = any(domain in sender_domain for domain in personal_domains)
    if has_personal_domain:
        # Check if it's actually promotional content from these platforms
        promo_matches = [kw for kw in promo_keywords if kw in combined_text]
        if promo_matches and len(promo_matches) >= 2:
            # Strong promotional signals - classify as Promotional
            return "Promotional", 0.90, promo_matches
        else:
            # Content/newsletter from these platforms - Personal/Other
            return "Personal/Other", 0.92, []
    
    # STEP 1: Check Banking/Financial FIRST (highest priority for financial safety)
    banking_matches = [kw for kw in banking_keywords if kw in combined_text]
    has_banking_domain = any(domain in sender_domain for domain in banking_domains)
    if banking_matches or has_banking_domain:
        matched_keywords = banking_matches
        confidence = 0.98 if (banking_matches and has_banking_domain) else 0.92 if banking_matches else 0.88
        return "Banking/Financial", confidence, matched_keywords
    
    # STEP 2: Check Shopping/Orders
    shopping_matches = [kw for kw in shopping_keywords if kw in combined_text]
    has_shopping_domain = any(domain in sender_domain for domain in shopping_domains)
    if shopping_matches or has_shopping_domain:
        matched_keywords = shopping_matches
        confidence = 0.96 if (shopping_matches and has_shopping_domain) else 0.90 if shopping_matches else 0.85
        return "Shopping/Orders", confidence, matched_keywords
    
    # STEP 3: Check Work/Career
    work_matches = [kw for kw in work_keywords if kw in combined_text]
    has_work_domain = any(domain in sender_domain for domain in work_domains)
    if work_matches or has_work_domain:
        matched_keywords = work_matches
        confidence = 0.94 if (work_matches and has_work_domain) else 0.88 if work_matches else 0.82
        return "Work/Career", confidence, matched_keywords
    
    # STEP 4: Check for promotional content
    promo_matches = [kw for kw in promo_keywords if kw in combined_text]
    if promo_matches:
        matched_keywords = promo_matches
        return "Promotional", 0.91, matched_keywords
    
    # STEP 5: Check Personal/Other
    personal_matches = [kw for kw in personal_keywords if kw in combined_text]
    if personal_matches:
        matched_keywords = personal_matches
        return "Personal/Other", 0.85, matched_keywords
    
    return None, 0.0, []


def classify_with_ml(subject, sender, body_snippet, features):
    """
    Advanced ML-based classification using zero-shot learning with MNLI.
    Reduced to 5 categories for better accuracy (Professor's recommendation).
    Returns (category, confidence, all_scores).
    """
    classifier = get_ml_classifier()
    if not classifier:
        return "Other", 0.5, {}
    
    # Construct optimized text for ML analysis
    sender_domain = features['sender_domain']
    text_to_analyze = f"From: {sender_domain}\nSubject: {subject}\nContent: {body_snippet[:300]}"
    
    # IMPROVED PROMPTS - More specific and context-aware
    # Using proper MNLI hypothesis format with clear distinctions
    candidate_labels = [
        "This email is a bank transaction alert, credit card statement, payment notification, or financial account update from a bank or payment service",
        "This email is an order confirmation, shipping notification, delivery tracking update, or purchase receipt from an online store or delivery service",
        "This email is a job application, interview invitation, professional networking message, work meeting, or career opportunity from a company or recruiter",
        "This email is a marketing campaign, sales promotion, discount offer, advertising message, or commercial deal trying to sell products or services",
        "This email is a personal newsletter, social media notification, content update, holiday greeting, product announcement, or general information from a service or platform"
    ]
    
    label_mapping = {
        "This email is a bank transaction alert, credit card statement, payment notification, or financial account update from a bank or payment service": "Banking/Financial",
        "This email is an order confirmation, shipping notification, delivery tracking update, or purchase receipt from an online store or delivery service": "Shopping/Orders",
        "This email is a job application, interview invitation, professional networking message, work meeting, or career opportunity from a company or recruiter": "Work/Career",
        "This email is a marketing campaign, sales promotion, discount offer, advertising message, or commercial deal trying to sell products or services": "Promotional",
        "This email is a personal newsletter, social media notification, content update, holiday greeting, product announcement, or general information from a service or platform": "Personal/Other"
    }
    
    try:
        ml_result = classifier(text_to_analyze, candidate_labels, multi_label=False)
        
        best_match = ml_result['labels'][0]
        confidence = ml_result['scores'][0]
        
        all_scores = {label_mapping.get(label, label): float(score) 
                     for label, score in zip(ml_result['labels'], ml_result['scores'])}
        
        category = label_mapping.get(best_match, "Other")
        
        return category, confidence, all_scores
        
    except Exception as e:
        print(f"ML classification error: {e}")
        return "Other", 0.5, {}


def analyze_sentiment(subject, body_snippet):
    """
    Sentiment analysis to understand email tone.
    Returns (sentiment_label, confidence_score).
    """
    sentiment_analyzer = get_sentiment_analyzer()
    if not sentiment_analyzer:
        return "NEUTRAL", 0.5
    
    try:
        sentiment_text = f"{subject}. {body_snippet}"[:512]
        sentiment_result = sentiment_analyzer(sentiment_text)[0]
        return sentiment_result['label'], float(sentiment_result['score'])
    except Exception as e:
        print(f"Sentiment analysis error: {e}")
        return "NEUTRAL", 0.5


def ensemble_classification(keyword_result, ml_result, features):
    """
    Enterprise-level ensemble method combining keyword and ML predictions.
    UPDATED: Strongly prioritize keyword matching over weak ML model.
    Keywords have proven to be more accurate than the undertrained TF-IDF model.
    """
    keyword_category, keyword_conf, matched_kw = keyword_result
    ml_category, ml_conf, ml_scores = ml_result
    
    # If keyword match exists with ANY confidence, trust it!
    # Keywords are rule-based and more reliable than the weak ML model
    if keyword_category and keyword_conf >= 0.80:
        return keyword_category, keyword_conf, ml_scores, 'keyword'
    
    # Only use ML if:
    # 1. No keyword match found, AND
    # 2. ML has reasonable confidence (>= 0.60)
    if not keyword_category and ml_conf >= 0.60:
        # Boost ML confidence if features support the prediction
        boosted_conf = ml_conf
        
        if ml_category == "Banking/Financial" and features['has_currency']:
            boosted_conf = min(0.95, ml_conf + 0.15)
        elif ml_category == "Shopping/Orders" and features['has_numbers']:
            boosted_conf = min(0.92, ml_conf + 0.12)
        elif ml_category == "Promotional" and features['has_urgency']:
            boosted_conf = min(0.90, ml_conf + 0.15)
        elif ml_category == "Work/Career" and features['sender_domain'] in ['linkedin.com', 'naukri.com']:
            boosted_conf = min(0.90, ml_conf + 0.15)
        
        return ml_category, boosted_conf, ml_scores, 'ml'
    
    # If we have a keyword match with lower confidence, still use it
    # (it's more reliable than low-confidence ML)
    if keyword_category:
        return keyword_category, keyword_conf, ml_scores, 'keyword'
    
    # Last resort: use ML even with low confidence, or default to Personal/Other
    if ml_conf >= 0.40:
        return ml_category, ml_conf, ml_scores, 'ml-uncertain'
    
    return "Personal/Other", 0.50, ml_scores, 'default'


def classify_email(subject, sender, body_snippet):
    """
    HYBRID classification: Fast keywords first, zero-shot only when needed.
    This is 5-10x faster while maintaining accuracy.
    """
    start_time = time.time()
    
    # Step 1: Feature Engineering
    features = extract_email_features(subject, sender, body_snippet)
    
    # Step 2: Try fast keyword matching first
    keyword_category, keyword_conf, matched_kw = classify_with_keywords(subject, sender, body_snippet, features)
    
    # If keywords are confident, skip slow zero-shot
    if keyword_category and keyword_conf >= 0.88:
        # High confidence keyword match - use it!
        final_confidence = min(0.95, keyword_conf + 0.05)
        method = 'keyword-fast'
        ml_scores = {}
        ml_category = keyword_category
    else:
        # Keywords uncertain - use zero-shot (slow but accurate)
        ml_classifier = get_ml_classifier()
        if ml_classifier:
            ml_category, ml_conf, ml_scores = classify_with_ml(subject, sender, body_snippet, features)
            method_base = 'zero-shot'
        else:
            # Fall back to TF-IDF
            ml_category, ml_conf, ml_scores = classify_with_tfidf(subject, sender, body_snippet)
            method_base = 'tfidf'
        
        # Aggressive confidence calibration for zero-shot
        if ml_conf >= 0.60:
            final_confidence = 0.85 + (ml_conf - 0.60) * 0.325
            method = f'{method_base}-high'
        elif ml_conf >= 0.45:
            final_confidence = 0.70 + (ml_conf - 0.45) * 1.0
            method = f'{method_base}-medium'
        elif ml_conf >= 0.30:
            final_confidence = 0.55 + (ml_conf - 0.30) * 1.0
            method = f'{method_base}-low'
        else:
            final_confidence = 0.45 + ml_conf * 0.333
            method = f'{method_base}-verylow'
        
        # Boost if keywords agree
        if keyword_category == ml_category and keyword_conf >= 0.85:
            final_confidence = min(0.98, final_confidence + 0.10)
            method = f'{method_base}-validated'
        
        # Feature-based boost
        if ml_category == "Banking/Financial" and features['has_currency']:
            final_confidence = min(0.98, final_confidence + 0.05)
        elif ml_category == "Shopping/Orders" and features['has_numbers']:
            final_confidence = min(0.95, final_confidence + 0.05)
        elif ml_category == "Promotional" and (features['has_percentage'] or features['exclamation_count'] >= 2):
            final_confidence = min(0.93, final_confidence + 0.05)
    
    # Sentiment Analysis
    sentiment, sentiment_score = analyze_sentiment(subject, body_snippet)
    
    processing_time = (time.time() - start_time) * 1000
    
    return {
        'category': ml_category,
        'confidence': round(final_confidence, 3),
        'sentiment': sentiment,
        'sentiment_score': round(sentiment_score, 3),
        'method': method,
        'processing_time_ms': round(processing_time, 2),
        'all_scores': ml_scores,
        'features': features,
        'matched_keywords': matched_kw
    }

def get_or_create_label(service, label_name):
    """Gets the ID of a label by name, creating it if it doesn't exist."""
    try:
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        for label in labels:
            if label['name'] == label_name:
                return label['id']
        
        # Create the label if it doesn't exist
        label_object = {
            'name': label_name,
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show'
        }
        created_label = service.users().labels().create(userId='me', body=label_object).execute()
        print(f"Created new label in Gmail: {label_name}")
        return created_label['id']
    except HttpError as error:
        print(f'An error occurred fetching/creating label {label_name}: {error}')
        return None

def process_emails(service, max_results=50, query="in:inbox category:promotions OR is:unread"):
    """
    Fetches emails based on a query, classifies them with metrics, and applies labels. 
    Optimized with batch processing. Uses TF-IDF as primary classifier.
    Rate-limited to avoid Gmail API quota issues.
    """
    start_time = time.time()
    
    # Dynamically create labels based on what the model predicts
    # This allows the model to use any categories it learned during training
    label_ids = {}
            
    try:
        print(f"\nScanning inbox (Query: '{query}', Max: {max_results})...")
        
        # Rate-limited API call
        @rate_limited_api_call
        def list_messages():
            return service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        
        results = list_messages()
        messages = results.get('messages', [])
        
        if not messages:
            print('No messages found matching query.')
            return {
                'emails': [],
                'total_count': 0,
                'processing_time_ms': (time.time() - start_time) * 1000,
                'metrics': {}
            }
        
        print(f"Found {len(messages)} messages. Fetching metadata sequentially with rate limiting...")
        
        # Sequential fetch with rate limiting to avoid concurrent request errors
        message_data = []
        consecutive_errors = 0
        
        @rate_limited_api_call
        def get_message(msg_id):
            return service.users().messages().get(
                userId='me', 
                id=msg_id, 
                format='metadata', 
                metadataHeaders=['Subject', 'From', 'Date']
            ).execute()
        
        for i, msg in enumerate(messages):
            try:
                response = get_message(msg['id'])
                message_data.append(response)
                consecutive_errors = 0  # Reset error counter on success
                if (i + 1) % 10 == 0:
                    print(f"Fetched {i + 1}/{len(messages)} messages...")
            except HttpError as error:
                if error.resp.status == 429:
                    consecutive_errors += 1
                    print(f"Rate limit hit on message {i + 1}. Pausing for {consecutive_errors * 5} seconds...")
                    time.sleep(consecutive_errors * 5)  # Increase pause with each consecutive error
                else:
                    print(f"Error fetching message {msg['id']}: {error}")
                continue
        
        print(f"Fetched {len(message_data)} messages. Starting classification...")
        
        processed_emails = []
        classification_metrics = {
            'total_classification_time_ms': 0,
            'avg_classification_time_ms': 0,
            'category_distribution': {},
            'sentiment_distribution': {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0},
            'method_distribution': {'keyword': 0, 'ml': 0, 'ensemble': 0, 'uncertain': 0},
            'avg_confidence': 0.0
        }
        
        total_confidence = 0.0
        
        for msg in message_data:
            headers = msg['payload']['headers']
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
            sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown Sender')
            date = next((header['value'] for header in headers if header['name'] == 'Date'), '')
            snippet = msg.get('snippet', '')
            
            # Classify the message with enhanced metrics
            classification_result = classify_email(subject, sender, snippet)
            category = classification_result['category']
            confidence = classification_result['confidence']
            sentiment = classification_result.get('sentiment', 'NEUTRAL')
            
            # Update metrics
            classification_metrics['total_classification_time_ms'] += classification_result['processing_time_ms']
            classification_metrics['category_distribution'][category] = \
                classification_metrics['category_distribution'].get(category, 0) + 1
            classification_metrics['sentiment_distribution'][sentiment] = \
                classification_metrics['sentiment_distribution'].get(sentiment, 0) + 1
            # Use .get() to handle any method type dynamically
            method = classification_result['method']
            classification_metrics['method_distribution'][method] = \
                classification_metrics['method_distribution'].get(method, 0) + 1
            total_confidence += confidence
            
            # Apply labels to Gmail with rate limiting
            # Create label on-demand if it doesn't exist yet
            @rate_limited_api_call
            def modify_message(msg_id, body):
                return service.users().messages().modify(userId='me', id=msg_id, body=body).execute()
            
            # Get or create label for this category
            if category not in label_ids:
                label_id = get_or_create_label(service, category)
                if label_id:
                    label_ids[category] = label_id
            
            if category in label_ids:
                mod_body = {
                    'addLabelIds': [label_ids[category]],
                    'removeLabelIds': ['UNREAD']
                }
                modify_message(msg['id'], mod_body)
            else:
                mod_body = {
                    'removeLabelIds': ['UNREAD']
                }
                modify_message(msg['id'], mod_body)
                
            processed_emails.append({
                "id": msg['id'],
                "subject": subject,
                "sender": sender,
                "date": date,
                "category": category,
                "confidence": round(confidence, 3),
                "sentiment": sentiment,
                "sentiment_score": round(classification_result.get('sentiment_score', 0.5), 3),
                "snippet": snippet,
                "processing_time_ms": round(classification_result['processing_time_ms'], 2),
                "all_scores": classification_result.get('all_scores', {})
            })
        
        # Calculate final metrics
        if processed_emails:
            classification_metrics['avg_classification_time_ms'] = \
                classification_metrics['total_classification_time_ms'] / len(processed_emails)
            classification_metrics['avg_confidence'] = total_confidence / len(processed_emails)
        
        total_time = (time.time() - start_time) * 1000
        
        print(f"[OK] Processed {len(processed_emails)} emails in {total_time:.2f}ms")
        print(f"  Avg classification time: {classification_metrics['avg_classification_time_ms']:.2f}ms")
        print(f"  Avg confidence: {classification_metrics['avg_confidence']:.2%}")
        
        return {
            'emails': processed_emails,
            'total_count': len(processed_emails),
            'processing_time_ms': round(total_time, 2),
            'metrics': classification_metrics
        }
                
    except HttpError as error:
        print(f'An error occurred processing emails: {error}')
        return {
            'emails': [],
            'total_count': 0,
            'processing_time_ms': (time.time() - start_time) * 1000,
            'metrics': {},
            'error': str(error)
        }

def delete_messages(service, message_ids):
    """
    Moves emails to trash (soft delete) or permanently deletes them.
    Note: Permanent deletion requires 'https://mail.google.com/' scope.
    With 'gmail.modify' scope, we can only trash emails.
    Rate-limited to avoid API quota issues.
    """
    try:
        if not message_ids:
            return 0
        
        # Try permanent deletion first (requires full Gmail scope)
        @rate_limited_api_call
        def batch_delete():
            return service.users().messages().batchDelete(
                userId='me',
                body={'ids': message_ids}
            ).execute()
        
        try:
            batch_delete()
            print(f"Permanently deleted {len(message_ids)} messages.")
            return len(message_ids)
        except HttpError as perm_error:
            # If permanent deletion fails due to insufficient permissions,
            # fall back to moving to trash (works with gmail.modify scope)
            if 'insufficientPermissions' in str(perm_error):
                print("Insufficient permissions for permanent deletion. Moving to trash instead...")
                deleted_count = 0
                
                @rate_limited_api_call
                def trash_message(msg_id):
                    return service.users().messages().trash(userId='me', id=msg_id).execute()
                
                for msg_id in message_ids:
                    try:
                        trash_message(msg_id)
                        deleted_count += 1
                    except HttpError as trash_error:
                        print(f"Error trashing message {msg_id}: {trash_error}")
                print(f"Moved {deleted_count} messages to trash.")
                return deleted_count
            else:
                raise perm_error
                
    except HttpError as error:
        print(f"An error occurred deleting messages: {error}")
        return 0

def archive_messages(service, message_ids):
    """
    Archives emails by removing the INBOX label.
    This moves emails out of the inbox without deleting them.
    Rate-limited to avoid API quota issues.
    """
    try:
        if not message_ids:
            return 0
        
        archived_count = 0
        
        @rate_limited_api_call
        def modify_message(msg_id):
            return service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['INBOX']}
            ).execute()
        
        for msg_id in message_ids:
            try:
                modify_message(msg_id)
                archived_count += 1
            except HttpError as error:
                print(f"Error archiving message {msg_id}: {error}")
        
        print(f"Archived {archived_count} messages.")
        return archived_count
                
    except HttpError as error:
        print(f"An error occurred archiving messages: {error}")
        return 0

def clean_inbox():
    """Kept for backwards compatibility if someone runs the script directly."""
    print("Starting Email Cleaner Assistant in terminal mode...")
    service = authenticate_gmail("default")
    
    if service:
        print("Assistant is ready.")
        import time
        while True:
            processed = process_emails(service)
            if processed:
                print(f"Processed {len(processed)} emails.")
            print("\nWaiting for 60 seconds before checking again...")
            time.sleep(60)

if __name__ == "__main__":
    clean_inbox()
