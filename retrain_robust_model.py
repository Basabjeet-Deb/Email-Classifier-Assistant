"""
Robust TF-IDF email classifier training pipeline.
Designed to handle real-world email noise and generalize better.
"""
import re
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from scipy.sparse import hstack
import joblib
from collections import Counter
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))
from backend.utils.robust_preprocessor import RobustEmailPreprocessor

# Paths
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)
MODEL_PATH = MODELS_DIR / "tfidf_classifier.pkl"


def generate_synthetic_emails():
    """Generate synthetic realistic emails for robustness."""
    synthetic_data = []
    
    # Transactional examples
    transactional = [
        ("orders@amazon.com", "Your order has shipped", "Your package will arrive tomorrow. Track it here. Order #12345"),
        ("noreply@paypal.com", "Payment received", "You received a payment of $29.99 from John Doe"),
        ("receipts@uber.com", "Your trip receipt", "Thanks for riding with Uber. Your fare was $15.50"),
        ("billing@netflix.com", "Your Netflix bill", "Your monthly subscription of $12.99 has been charged"),
        ("orders@flipkart.com", "Order confirmed", "Your order #98765 has been confirmed and will be delivered soon"),
    ] * 100  # 500 samples
    
    for sender, subject, body in transactional:
        synthetic_data.append((sender, subject, body, 'Transactional'))
    
    # Promotional examples
    promotional = [
        ("deals@amazon.com", "Limited time offer - 50% off", "Shop now and save big on electronics. Sale ends tonight!"),
        ("marketing@flipkart.com", "Flash sale today only", "Get up to 70% discount on fashion. Don't miss out!"),
        ("offers@swiggy.com", "Free delivery on your next order", "Use code FREE50 and get free delivery"),
        ("sales@myntra.com", "Mega sale - Up to 80% off", "Biggest sale of the year. Shop now!"),
        ("promo@zomato.com", "Special discount just for you", "Get 40% off on your next order"),
    ] * 100  # 500 samples
    
    for sender, subject, body in promotional:
        synthetic_data.append((sender, subject, body, 'Promotional'))
    
    # Social examples
    social = [
        ("noreply@linkedin.com", "John mentioned you in a comment", "John Smith mentioned you in a comment on his post"),
        ("notify@facebook.com", "You have 5 new friend requests", "Check out who wants to connect with you"),
        ("updates@twitter.com", "Your tweet got 50 likes", "Your recent tweet is getting attention"),
        ("noreply@instagram.com", "Sarah liked your photo", "Sarah and 10 others liked your recent photo"),
        ("notifications@reddit.com", "New reply to your comment", "Someone replied to your comment in r/python"),
    ] * 100  # 500 samples
    
    for sender, subject, body in social:
        synthetic_data.append((sender, subject, body, 'Social'))
    
    # Important examples
    important = [
        ("hr@company.com", "URGENT: Team meeting tomorrow", "Please confirm your attendance for the important meeting"),
        ("boss@work.com", "Action required: Project deadline", "The project deadline is approaching. Please update status"),
        ("security@bank.com", "Security alert on your account", "We detected unusual activity. Please verify immediately"),
        ("admin@company.com", "Password reset required", "Your password will expire in 24 hours. Please reset now"),
        ("recruiter@company.com", "Interview scheduled", "Your interview is scheduled for tomorrow at 10 AM"),
    ] * 100  # 500 samples
    
    for sender, subject, body in important:
        synthetic_data.append((sender, subject, body, 'Important'))
    
    # Spam examples
    spam = [
        ("winner@lottery.com", "Congratulations! You won $1,000,000", "Click here to claim your prize now! Limited time offer!"),
        ("prince@nigeria.com", "Urgent business proposal", "I am a Nigerian prince and need your help transferring money"),
        ("claim@prize.com", "You've been selected for a free gift", "Claim your free iPhone now! Click here immediately!"),
        ("money@scam.com", "Make $5000 working from home", "Easy money! No experience needed! Start today!"),
        ("verify@phishing.com", "Verify your account now", "Your account will be suspended. Click here to verify!"),
    ] * 100  # 500 samples
    
    for sender, subject, body in spam:
        synthetic_data.append((sender, subject, body, 'Spam'))
    
    return synthetic_data


def train_robust_model():
    """Train robust TF-IDF model with all enhancements."""
    print("="*80)
    print("ROBUST EMAIL CLASSIFIER TRAINING")
    print("="*80)
    
    # Initialize preprocessor
    preprocessor = RobustEmailPreprocessor()
    
    # Load original dataset
    print("\n1. Loading original dataset...")
    dataset_path = BASE_DIR / "email_intent_dataset_5000.csv"
    df = pd.read_csv(dataset_path)
    
    original_data = []
    for _, row in df.iterrows():
        text = row['text']
        label = row['label']
        # Infer sender and split text
        sender = 'unknown@email.com'
        subject = text[:100]
        body = text
        original_data.append((sender, subject, body, label))
    
    print(f"[OK] Loaded {len(original_data)} original samples")
    
    # Load user feedback data
    print("\n2. Loading user feedback data...")
    feedback_path = BASE_DIR / "data" / "feedback_dataset.csv"
    feedback_data = []
    
    if feedback_path.exists():
        try:
            feedback_df = pd.read_csv(feedback_path)
            # Skip the first 3 test rows
            feedback_df = feedback_df[3:]
            
            for _, row in feedback_df.iterrows():
                sender = row.get('sender', 'unknown@email.com')
                subject = row.get('subject', '')
                body = row.get('body', '')
                correct_category = row.get('correct_category', '')
                
                if correct_category and correct_category.strip():
                    feedback_data.append((sender, subject, body, correct_category))
            
            print(f"[OK] Loaded {len(feedback_data)} user feedback samples")
            
            # Show feedback distribution
            if feedback_data:
                feedback_labels = [item[3] for item in feedback_data]
                feedback_counts = Counter(feedback_labels)
                print("\nUser feedback distribution:")
                for label, count in sorted(feedback_counts.items()):
                    print(f"  {label}: {count} samples")
        except Exception as e:
            print(f"[WARNING] Failed to load feedback data: {e}")
    else:
        print("[INFO] No feedback data found")
    
    # Combine original + feedback
    original_data.extend(feedback_data)
    print(f"\n[OK] Total dataset with feedback: {len(original_data)} samples")
    
    # Generate synthetic data
    print("\n3. Generating synthetic realistic emails...")
    synthetic_data = generate_synthetic_emails()
    print(f"[OK] Generated {len(synthetic_data)} synthetic samples")
    
    # Combine datasets
    all_data = original_data + synthetic_data
    print(f"\n[OK] Total training data: {len(all_data)} samples")
    
    # Create robust texts
    print("\n4. Creating robust text features...")
    robust_texts = []
    labels = []
    
    for sender, subject, body, label in all_data:
        robust_text = preprocessor.create_robust_text(sender, subject, body)
        robust_texts.append(robust_text)
        labels.append(label)
    
    # Check distribution
    label_counts = Counter(labels)
    print("\nClass distribution:")
    for label, count in sorted(label_counts.items()):
        print(f"  {label}: {count} samples ({count/len(labels)*100:.1f}%)")
    
    # Train/test split
    print("\n5. Splitting dataset (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        robust_texts, labels,
        test_size=0.2,
        random_state=42,
        stratify=labels
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    
    # Create dual vectorizers (word + char ngrams)
    print("\n6. Creating dual TF-IDF vectorizers...")
    
    # Word-level vectorizer
    word_vectorizer = TfidfVectorizer(
        analyzer='word',
        ngram_range=(1, 2),
        max_features=15000,
        min_df=2,
        max_df=0.9,
        sublinear_tf=True,
        strip_accents='unicode'
    )
    
    # Character-level vectorizer (captures spelling variations)
    char_vectorizer = TfidfVectorizer(
        analyzer='char',
        ngram_range=(3, 5),
        max_features=8000,
        min_df=2,
        max_df=0.9,
        sublinear_tf=True
    )
    
    # Transform training data
    print("\n7. Transforming text to features...")
    X_train_word = word_vectorizer.fit_transform(X_train)
    X_train_char = char_vectorizer.fit_transform(X_train)
    X_train_combined = hstack([X_train_word, X_train_char])
    
    X_test_word = word_vectorizer.transform(X_test)
    X_test_char = char_vectorizer.transform(X_test)
    X_test_combined = hstack([X_test_word, X_test_char])
    
    print(f"[OK] Combined features: {X_train_combined.shape[1]} dimensions")
    
    # Train LinearSVC
    print("\n8. Training LinearSVC...")
    
    base_model = LinearSVC(
        C=1.0,
        max_iter=2000,
        class_weight='balanced',
        random_state=42
    )
    
    base_model.fit(X_train_combined, y_train)
    
    # Calibrate for probability estimates on full training set
    print("\n9. Calibrating probabilities...")
    model = CalibratedClassifierCV(
        base_model,
        method='sigmoid',
        cv='prefit'  # Use prefit model
    )
    
    model.fit(X_train_combined, y_train)
    
    # Cross-validation on base model
    print("\n10. Performing 5-fold cross-validation...")
    cv_scores = cross_val_score(base_model, X_train_combined, y_train, cv=5, scoring='accuracy')
    print(f"CV Accuracy: {cv_scores.mean()*100:.2f}% (+/- {cv_scores.std()*100:.2f}%)")
    
    # Evaluate on test set
    print("\n" + "="*80)
    print("MODEL EVALUATION")
    print("="*80)
    
    y_pred = model.predict(X_test_combined)
    y_pred_proba = model.predict_proba(X_test_combined)
    
    # Accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nTest Accuracy: {accuracy*100:.2f}%")
    
    # Average confidence
    avg_confidence = np.mean(np.max(y_pred_proba, axis=1))
    print(f"Average Confidence: {avg_confidence*100:.2f}%")
    
    # Classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    
    # Confusion matrix
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
    print(f"Classes: {list(model.classes_)}")
    print(cm)
    
    print("="*80)
    
    # Save model and vectorizers
    print("\n11. Saving model and vectorizers...")
    model_data = {
        'model': model,
        'word_vectorizer': word_vectorizer,
        'char_vectorizer': char_vectorizer,
        'preprocessor': preprocessor,
        'classes': model.classes_,
        'accuracy': accuracy,
        'avg_confidence': avg_confidence
    }
    
    joblib.dump(model_data, MODEL_PATH)
    print(f"[OK] Model saved to: {MODEL_PATH}")
    
    print("\n" + "="*80)
    print("[SUCCESS] ROBUST MODEL TRAINING COMPLETE")
    print("="*80)
    print(f"Test Accuracy: {accuracy*100:.2f}%")
    print(f"Average Confidence: {avg_confidence*100:.2f}%")
    print(f"CV Accuracy: {cv_scores.mean()*100:.2f}% (+/- {cv_scores.std()*100:.2f}%)")
    print(f"Total Features: {X_train_combined.shape[1]}")
    print(f"Training Samples: {len(X_train)}")
    print("="*80)
    
    return True


if __name__ == "__main__":
    train_robust_model()
