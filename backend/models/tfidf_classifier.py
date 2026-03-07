"""
TF-IDF + Logistic Regression classifier for efficient email classification.
Memory-efficient alternative to transformer models.
"""
import pickle
from typing import Tuple, Dict
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import numpy as np

from backend.config import TFIDF_MODEL_PATH, CATEGORIES


class TFIDFClassifier:
    """
    TF-IDF + Logistic Regression classifier.
    Fast, accurate, and memory-efficient (~10MB RAM).
    """
    
    def __init__(self):
        """Initialize the classifier."""
        self.model = None
        self.is_loaded = False
    
    def load_model(self) -> bool:
        """
        Load the trained model from disk.
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        if self.is_loaded:
            return True
        
        try:
            if TFIDF_MODEL_PATH.exists():
                print(f"Loading TF-IDF model from {TFIDF_MODEL_PATH}...")
                with open(TFIDF_MODEL_PATH, 'rb') as f:
                    self.model = pickle.load(f)
                self.is_loaded = True
                print("TF-IDF model loaded successfully.")
                return True
            else:
                print("TF-IDF model not found. Training new model...")
                self.train_model()
                return True
        except Exception as e:
            print(f"Failed to load TF-IDF model: {e}")
            return False
    
    def train_model(self, texts: list = None, labels: list = None):
        """
        Train a new TF-IDF model.
        
        Args:
            texts: Training texts (optional, uses synthetic data if None)
            labels: Training labels (optional)
        """
        if texts is None or labels is None:
            texts, labels = self._get_training_data()
        
        print(f"Training TF-IDF model on {len(texts)} samples...")
        
        # Create pipeline with optimized hyperparameters
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=3000,
                ngram_range=(1, 3),
                stop_words='english',
                min_df=1,
                max_df=0.95,
                sublinear_tf=True,
                strip_accents='unicode'
            )),
            ('clf', LogisticRegression(
                max_iter=2000,
                multi_class='multinomial',
                solver='lbfgs',
                C=1.5,
                class_weight='balanced',
                random_state=42
            ))
        ])
        
        # Train
        self.model.fit(texts, labels)
        self.is_loaded = True
        
        # Save model
        self.save_model()
        print("TF-IDF model trained and saved successfully.")
    
    def save_model(self):
        """Save the trained model to disk."""
        if self.model is not None:
            TFIDF_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(TFIDF_MODEL_PATH, 'wb') as f:
                pickle.dump(self.model, f)
            print(f"Model saved to {TFIDF_MODEL_PATH}")
    
    def classify(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        """
        Classify text using TF-IDF model.
        
        Args:
            text: Text to classify
            
        Returns:
            Tuple of (category, confidence, all_scores)
        """
        if not self.is_loaded:
            self.load_model()
        
        if self.model is None:
            return "Personal/Other", 0.5, {}
        
        try:
            # Predict
            category = self.model.predict([text])[0]
            probabilities = self.model.predict_proba([text])[0]
            
            # Get all scores
            classes = self.model.classes_
            all_scores = {cls: float(prob) for cls, prob in zip(classes, probabilities)}
            
            # Get confidence for predicted category
            confidence = max(probabilities)
            
            return category, confidence, all_scores
        except Exception as e:
            print(f"TF-IDF classification error: {e}")
            return "Personal/Other", 0.5, {}
    
    def _get_training_data(self) -> Tuple[list, list]:
        """
        Get synthetic training data for initial model.
        In production, this should be replaced with real labeled data.
        
        Returns:
            Tuple of (texts, labels)
        """
        # Augmented training data (200+ examples)
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
        
        return texts, labels


# Global instance
_tfidf_classifier = None


def get_tfidf_classifier() -> TFIDFClassifier:
    """Get the global TF-IDF classifier instance."""
    global _tfidf_classifier
    if _tfidf_classifier is None:
        _tfidf_classifier = TFIDFClassifier()
    return _tfidf_classifier
