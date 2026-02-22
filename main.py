import os.path
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

_ml_pipeline = None
_sentiment_pipeline = None
_classification_cache = {}

def get_ml_classifier():
    """Lazily load the HuggingFace zero-shot classification pipeline."""
    global _ml_pipeline
    if _ml_pipeline is None:
        try:
            import numpy as np
            print(f"Numpy version: {np.__version__}")
            from transformers import pipeline
            print("Loading ML Classification Model (DistilBERT zero-shot)...")
            # Using a fast, lightweight distilbert MNLI model for zero-shot text classification
            _ml_pipeline = pipeline(
                "zero-shot-classification", 
                model="typeform/distilbert-base-uncased-mnli", 
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
    Rule-based classification using expanded keyword matching and sender analysis.
    Returns (category, confidence, matched_keywords) or (None, 0, []) if no match.
    """
    combined_text = f"{subject} {body_snippet}".lower()
    sender_lower = sender.lower()
    sender_domain = features['sender_domain'].lower()
    
    # Expanded keyword sets with weights
    banking_keywords = [
        'account statement', 'transaction', 'balance', 'credit card', 'debit card',
        'payment', 'netbanking', 'upi', 'neft', 'rtgs', 'imps',
        'account alert', 'credited', 'debited', 'withdrawal', 'deposit',
        'statement for', 'minimum balance', 'overdraft', 'loan', 'emi', 'interest'
    ]
    banking_domains = ['bank', 'sbi', 'hdfc', 'icici', 'axis', 'kotak', 'paytm', 'phonepe', 'gpay', 'citi', 'hsbc']
    
    receipt_keywords = [
        'order confirmation', 'receipt', 'invoice', 'shipped', 'delivery',
        'tracking', 'your order', 'purchase', 'payment successful', 'order placed',
        'dispatched', 'out for delivery', 'delivered', 'order #', 'order number',
        'thank you for your order', 'shipment', 'package', 'courier', 'tracking number'
    ]
    receipt_domains = ['amazon', 'flipkart', 'myntra', 'swiggy', 'zomato', 'uber', 'ola', 'ebay', 'shopify']
    
    # PRIORITY: Check promotional keywords FIRST (before checking sender domain)
    promo_keywords = [
        'special offer', 'discount', 'sale', 'limited time', 'offer expires',
        'buy now', 'shop now', 'deal', 'save', 'free trial', 'subscribe now',
        'unsubscribe', 'register now', 'sign up', 'join now', 'exclusive offer',
        'promotional', 'advertisement', 'marketing', 'off %', '% off', 'claim your',
        'dont miss', "don't miss", 'last chance', 'hurry', 'act now', 'limited offer',
        'flash sale', 'clearance', 'mega sale', 'biggest sale', 'offer valid', 'promo code',
        'apply now', 'get ready', 'hot tip', 'register today', 'join the', 'demat account',
        'free', 'click here', 'learn more', 'find out', 'discover', 'explore'
    ]
    
    newsletter_keywords = [
        'newsletter', 'weekly digest', 'monthly update', 'learn', 'course',
        'training', 'tutorial', 'masterclass', 'certification', 'skills',
        'webinar', 'workshop', 'session', 'class', 'lesson', 'module', 'udemy', 'coursera'
    ]
    
    work_keywords = [
        'meeting', 'interview', 'job', 'career', 'resume', 'cv', 'application',
        'position', 'opportunity', 'hiring', 'recruitment', 'linkedin', 'naukri',
        'project', 'deadline', 'task', 'team', 'colleague', 'conference call'
    ]
    
    social_keywords = [
        'facebook', 'twitter', 'instagram', 'linkedin', 'notification',
        'liked your', 'commented on', 'tagged you', 'friend request',
        'connection request', 'mentioned you', 'shared', 'posted', 'follow'
    ]
    
    # Check each category with domain and keyword matching
    matched_keywords = []
    
    # STEP 1: Check for promotional content FIRST (highest priority to avoid false positives)
    promo_matches = [kw for kw in promo_keywords if kw in combined_text]
    newsletter_matches = [kw for kw in newsletter_keywords if kw in combined_text]
    
    if promo_matches:
        # Even if sender is a bank/company, if content is promotional, classify as such
        if newsletter_matches or 'course' in combined_text or 'webinar' in combined_text:
            matched_keywords = newsletter_matches
            return "Newsletters", 0.87, matched_keywords
        else:
            matched_keywords = promo_matches
            return "Spam/Promotional", 0.91, matched_keywords
    
    # STEP 2: Check Banking/Financial (only if NOT promotional)
    banking_matches = [kw for kw in banking_keywords if kw in combined_text]
    if banking_matches or any(domain in sender_domain for domain in banking_domains):
        # Double-check it's not promotional even if from bank
        if not any(kw in combined_text for kw in ['apply now', 'register', 'join', 'offer', 'free']):
            matched_keywords = banking_matches
            confidence = 0.95 if banking_matches else 0.85  # Lower confidence if only domain match
            return "Banking/Financial", confidence, matched_keywords
    
    # STEP 3: Check Receipts/Orders
    receipt_matches = [kw for kw in receipt_keywords if kw in combined_text]
    if receipt_matches or any(domain in sender_domain for domain in receipt_domains):
        matched_keywords = receipt_matches
        confidence = 0.93 if receipt_matches else 0.85
        return "Receipts/Orders", confidence, matched_keywords
    
    # STEP 4: Check Work/Career (but not job promotional emails)
    work_matches = [kw for kw in work_keywords if kw in combined_text]
    if work_matches:
        # If it's from job sites with promotional language, it's promotional
        if any(domain in sender_domain for domain in ['indeed', 'naukri', 'linkedin']) and \
           any(kw in combined_text for kw in ['apply now', 'hot tip', 'register']):
            return "Spam/Promotional", 0.89, promo_matches
        matched_keywords = work_matches
        return "Work/Career", 0.88, matched_keywords
    
    # STEP 5: Check Social Updates
    social_matches = [kw for kw in social_keywords if kw in combined_text]
    if social_matches:
        matched_keywords = social_matches
        return "Social/Updates", 0.90, matched_keywords
    
    return None, 0.0, []


def classify_with_ml(subject, sender, body_snippet, features):
    """
    Advanced ML-based classification using zero-shot learning.
    Returns (category, confidence, all_scores).
    """
    classifier = get_ml_classifier()
    if not classifier:
        return "Other", 0.5, {}
    
    # Construct optimized text for ML analysis
    # Include sender domain as it's a strong signal
    sender_domain = features['sender_domain']
    text_to_analyze = f"From: {sender_domain}\nSubject: {subject}\nContent: {body_snippet[:300]}"
    
    # Optimized candidate labels for better accuracy
    candidate_labels = [
        "Banking, financial transactions, money, account statements",
        "Shopping receipts, order confirmations, delivery tracking",
        "Work, career, job opportunities, professional meetings",
        "Social media notifications, friend updates, connections",
        "Educational newsletters, courses, learning materials",
        "Important personal emails, travel, security alerts",
        "Marketing promotions, advertisements, sales offers"
    ]
    
    label_mapping = {
        "Banking, financial transactions, money, account statements": "Banking/Financial",
        "Shopping receipts, order confirmations, delivery tracking": "Receipts/Orders",
        "Work, career, job opportunities, professional meetings": "Work/Career",
        "Social media notifications, friend updates, connections": "Social/Updates",
        "Educational newsletters, courses, learning materials": "Newsletters",
        "Important personal emails, travel, security alerts": "Personal/Important",
        "Marketing promotions, advertisements, sales offers": "Spam/Promotional"
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
    Uses weighted voting and confidence calibration for optimal accuracy.
    """
    keyword_category, keyword_conf, matched_kw = keyword_result
    ml_category, ml_conf, ml_scores = ml_result
    
    # If keyword match is strong, trust it (high precision)
    if keyword_category and keyword_conf >= 0.88:
        # But still consider ML if it strongly disagrees
        if ml_category != keyword_category and ml_conf > 0.7:
            # Weighted ensemble: 70% keyword, 30% ML
            final_conf = (keyword_conf * 0.7) + (ml_conf * 0.3)
            # If ML is very confident, use ML category
            if ml_conf > keyword_conf:
                return ml_category, final_conf, ml_scores, 'ensemble'
        return keyword_category, keyword_conf, ml_scores, 'keyword'
    
    # If keyword match is weak or no match, use ML
    if ml_conf >= 0.35:
        # Boost ML confidence if features support the prediction
        boosted_conf = ml_conf
        
        # Feature-based confidence boosting
        if ml_category == "Banking/Financial" and features['has_currency']:
            boosted_conf = min(0.95, ml_conf + 0.10)
        elif ml_category == "Receipts/Orders" and features['has_numbers']:
            boosted_conf = min(0.92, ml_conf + 0.08)
        elif ml_category == "Spam/Promotional" and features['has_urgency']:
            boosted_conf = min(0.90, ml_conf + 0.10)
        elif ml_category == "Work/Career" and features['sender_domain'] in ['linkedin.com', 'naukri.com']:
            boosted_conf = min(0.90, ml_conf + 0.12)
        
        return ml_category, boosted_conf, ml_scores, 'ml'
    
    # Low confidence - mark as Other
    return "Other", max(keyword_conf, ml_conf), ml_scores, 'uncertain'


def classify_email(subject, sender, body_snippet):
    """
    Enterprise-level email classification using ensemble ML approach.
    Combines rule-based, ML, and sentiment analysis for high accuracy.
    """
    start_time = time.time()
    
    # Step 1: Feature Engineering
    features = extract_email_features(subject, sender, body_snippet)
    
    # Step 2: Rule-based Classification (fast, high precision)
    keyword_result = classify_with_keywords(subject, sender, body_snippet, features)
    
    # Step 3: ML Classification (slower, high recall)
    ml_result = classify_with_ml(subject, sender, body_snippet, features)
    
    # Step 4: Ensemble Decision
    category, confidence, all_scores, method = ensemble_classification(keyword_result, ml_result, features)
    
    # Step 5: Sentiment Analysis (parallel insight)
    sentiment, sentiment_score = analyze_sentiment(subject, body_snippet)
    
    processing_time = (time.time() - start_time) * 1000
    
    return {
        'category': category,
        'confidence': round(confidence, 3),
        'sentiment': sentiment,
        'sentiment_score': round(sentiment_score, 3),
        'method': method,
        'processing_time_ms': round(processing_time, 2),
        'all_scores': all_scores,
        'features': features,
        'matched_keywords': keyword_result[2] if keyword_result[0] else []
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
    """Fetches emails based on a query, classifies them with metrics, and applies labels. Optimized with batch processing."""
    start_time = time.time()
    
    # Ensure our labels exist
    label_names = [
        "Banking/Financial", "Spam/Promotional", "Personal/Important",
        "Receipts/Orders", "Work/Career", "Social/Updates", "Newsletters"
    ]
    label_ids = {}
    for name in label_names:
        l_id = get_or_create_label(service, name)
        if l_id:
            label_ids[name] = l_id
            
    try:
        print(f"\nScanning inbox (Query: '{query}', Max: {max_results})...")
        results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print('No messages found matching query.')
            return {
                'emails': [],
                'total_count': 0,
                'processing_time_ms': (time.time() - start_time) * 1000,
                'metrics': {}
            }
        
        print(f"Found {len(messages)} messages. Fetching metadata in batch...")
        
        # Batch fetch message metadata for speed
        from googleapiclient.http import BatchHttpRequest
        
        message_data = []
        
        def callback(request_id, response, exception):
            if exception:
                print(f"Error fetching message {request_id}: {exception}")
            else:
                message_data.append(response)
        
        # Create batch request for faster fetching
        batch = service.new_batch_http_request(callback=callback)
        for msg in messages:
            batch.add(service.users().messages().get(
                userId='me', 
                id=msg['id'], 
                format='metadata', 
                metadataHeaders=['Subject', 'From', 'Date']
            ))
        
        batch.execute()
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
            classification_metrics['method_distribution'][classification_result['method']] += 1
            total_confidence += confidence
            
            # Apply labels to Gmail
            if category in label_ids:
                mod_body = {
                    'addLabelIds': [label_ids[category]],
                    'removeLabelIds': ['UNREAD']
                }
                service.users().messages().modify(userId='me', id=msg['id'], body=mod_body).execute()
            else:
                mod_body = {
                    'removeLabelIds': ['UNREAD']
                }
                service.users().messages().modify(userId='me', id=msg['id'], body=mod_body).execute()
                
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
    """
    try:
        if not message_ids:
            return 0
        
        # Try permanent deletion first (requires full Gmail scope)
        try:
            service.users().messages().batchDelete(
                userId='me',
                body={'ids': message_ids}
            ).execute()
            print(f"Permanently deleted {len(message_ids)} messages.")
            return len(message_ids)
        except HttpError as perm_error:
            # If permanent deletion fails due to insufficient permissions,
            # fall back to moving to trash (works with gmail.modify scope)
            if 'insufficientPermissions' in str(perm_error):
                print("Insufficient permissions for permanent deletion. Moving to trash instead...")
                deleted_count = 0
                for msg_id in message_ids:
                    try:
                        service.users().messages().trash(userId='me', id=msg_id).execute()
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
