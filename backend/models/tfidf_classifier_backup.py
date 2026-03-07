"""
TF-IDF + Logistic Regression classifier for efficient email classification.
Memory-efficient alternative to transformer models.
"""
import pickle
import joblib
from typing import Tuple, Dict, List
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
        self._training_in_progress = False
    
    def load_model(self) -> bool:
        """
        Load the trained model from disk.
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        if self.is_loaded:
            return True
        
        # Prevent concurrent training
        if self._training_in_progress:
            print("Training already in progress, waiting...")
            return False
        
        try:
            if TFIDF_MODEL_PATH.exists():
                print(f"Loading TF-IDF model from {TFIDF_MODEL_PATH}...")
                with open(TFIDF_MODEL_PATH, 'rb') as f:
                    self.model = pickle.load(f)
                
                # Verify model is properly fitted
                if not hasattr(self.model, 'classes_'):
                    print("WARNING: Loaded model is not fitted. Retraining...")
                    TFIDF_MODEL_PATH.unlink()  # Delete corrupted model
                    return self.train_model()
                
                self.is_loaded = True
                print(f"✓ TF-IDF model loaded successfully. Classes: {len(self.model.classes_)}")
                return True
            else:
                print("TF-IDF model not found. Training new model...")
                return self.train_model()
        except Exception as e:
            print(f"Failed to load TF-IDF model: {e}")
            import traceback
            traceback.print_exc()
            # Try to train a new model
            if TFIDF_MODEL_PATH.exists():
                TFIDF_MODEL_PATH.unlink()  # Delete corrupted model
            return self.train_model()
    
    def train_model(self, texts: List[str] = None, labels: List[str] = None) -> bool:
        """
        Train a new TF-IDF model with proper validation.
        
        Args:
            texts: Training texts (optional, uses synthetic data if None)
            labels: Training labels (optional)
            
        Returns:
            True if training successful, False otherwise
        """
        if self._training_in_progress:
            print("Training already in progress")
            return False
        
        self._training_in_progress = True
        
        try:
            # Get training data
            if texts is None or labels is None:
                texts, labels = self._get_training_data()
            
            # CRITICAL: Validate dataset consistency
            if len(texts) != len(labels):
                print(f"WARNING: Dataset mismatch - texts: {len(texts)}, labels: {len(labels)}")
                min_len = min(len(texts), len(labels))
                texts = texts[:min_len]
                labels = labels[:min_len]
                print(f"Trimmed dataset to {min_len} samples")
            
            # Validate minimum samples
            if len(texts) < 10:
                print(f"ERROR: Not enough training samples ({len(texts)}). Need at least 10.")
                self._training_in_progress = False
                return False
            
            print(f"Training TF-IDF model on {len(texts)} samples...")
            print(f"Categories: {set(labels)}")
            
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
            
            # Verify model is fitted
            if not hasattr(self.model, 'classes_'):
                print("ERROR: Model training failed - not fitted")
                self._training_in_progress = False
                return False
            
            self.is_loaded = True
            
            # Save model
            self.save_model()
            
            print(f"✓ TF-IDF model trained successfully!")
            print(f"  - Training samples: {len(texts)}")
            print(f"  - Categories: {len(self.model.classes_)}")
            print(f"  - Model saved to: {TFIDF_MODEL_PATH}")
            
            self._training_in_progress = False
            return True
            
        except Exception as e:
            print(f"ERROR: TF-IDF training failed: {e}")
            import traceback
            traceback.print_exc()
            self._training_in_progress = False
            return False
    
    def save_model(self):
        """Save the trained model to disk."""
        if self.model is not None and hasattr(self.model, 'classes_'):
            try:
                TFIDF_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(TFIDF_MODEL_PATH, 'wb') as f:
                    pickle.dump(self.model, f)
                print(f"✓ Model saved to {TFIDF_MODEL_PATH}")
            except Exception as e:
                print(f"ERROR: Failed to save model: {e}")
        else:
            print("WARNING: Cannot save unfitted model")
    
    def classify(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        """
        Classify text using TF-IDF model.
        
        Args:
            text: Text to classify
            
        Returns:
            Tuple of (category, confidence, all_scores)
        """
        if not self.is_loaded:
            success = self.load_model()
            if not success:
                print("ERROR: TF-IDF model not available")
                return "Personal/Other", 0.5, {}
        
        if self.model is None:
            print("ERROR: TF-IDF model is None")
            return "Personal/Other", 0.5, {}
        
        # Verify model is fitted
        if not hasattr(self.model, 'classes_'):
            print("ERROR: TF-IDF model is not fitted")
            return "Personal/Other", 0.5, {}
        
        try:
            # Predict
            category = self.model.predict([text])[0]
            probabilities = self.model.predict_proba([text])[0]
            
            # Get all scores
            classes = self.model.classes_
            all_scores = {cls: float(prob) for cls, prob in zip(classes, probabilities)}
            
            # Get confidence for predicted category
            confidence = float(max(probabilities))
            
            return category, confidence, all_scores
        except Exception as e:
            print(f"TF-IDF classification error: {e}")
            import traceback
            traceback.print_exc()
            return "Personal/Other", 0.5, {}
    
    def _get_training_data(self) -> Tuple[List[str], List[str]]:
        """
        Load training data from intent dataset CSV.
        
        Returns:
            Tuple of (texts, labels) with guaranteed equal lengths
        """
        import csv
        from backend.config import BASE_DIR
        
        # Use the intent dataset
        csv_path = BASE_DIR / "email_intent_dataset_5000.csv"
        
        # Try to load from CSV first
        if csv_path.exists():
            try:
                print(f"Loading intent training data from {csv_path}...")
                texts = []
                labels = []
                
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        text = row.get('text', '').strip()
                        label = row.get('label', '').strip()
                        
                        # Only add if both exist
                        if text and label:
                            texts.append(text)
                            labels.append(label)
                
                # Validate dataset
                if len(texts) >= 10 and len(texts) == len(labels):
                    print(f"✓ Loaded {len(texts)} intent samples from CSV")
                    print(f"  Categories: {set(labels)}")
                    return texts, labels
                else:
                    print(f"WARNING: CSV data insufficient ({len(texts)} samples)")
            except Exception as e:
                print(f"ERROR loading CSV: {e}")
                import traceback
                traceback.print_exc()
        
        # Fallback to synthetic data
        print("WARNING: Intent dataset not found, using synthetic data...")
        return self._get_synthetic_training_data()
    
    def _get_synthetic_training_data(self) -> Tuple[List[str], List[str]]:
        """
        Generate synthetic intent-based training data as fallback.
        
        Returns:
            Tuple of (texts, labels) with guaranteed equal lengths
        """
        # Build dataset with explicit pairing
        dataset = []
        
        # Important (50 examples) - Requires immediate attention
        important_texts = [
            "Interview invitation for Software Engineer position",
            "Your account has been locked due to suspicious activity",
            "Urgent: Project deadline moved to tomorrow",
            "Job offer from Google - Action required",
            "Security alert: New login from unknown device",
            "Your password will expire in 24 hours",
            "Meeting with CEO scheduled for today",
            "Critical bug found in production",
            "Your application has been shortlisted",
            "Account verification required immediately",
            "Important update regarding your subscription",
            "Your payment method needs updating",
            "Deadline reminder: Submit report by EOD",
            "Emergency: Server downtime detected",
            "Your resume has been reviewed",
            "Interview scheduled for tomorrow 10 AM",
            "Offer letter attached - Please review",
            "Account suspension notice",
            "Urgent action required on your account",
            "Your contract is expiring soon",
            "Important notice from HR department",
            "Project milestone review meeting",
            "Critical security update required",
            "Your application status has changed",
            "Immediate response needed for client",
            "Account alert: Unusual activity detected",
            "Your verification code expires soon",
            "Important tax document attached",
            "Urgent: Client meeting rescheduled",
            "Your account needs verification",
            "Critical system maintenance tonight",
            "Interview feedback request",
            "Your proposal has been accepted",
            "Important policy update",
            "Account recovery instructions",
            "Your subscription is expiring",
            "Urgent team meeting called",
            "Important announcement from management",
            "Your access will be revoked soon",
            "Critical update required",
            "Your application requires documents",
            "Important deadline approaching",
            "Account security review needed",
            "Your profile needs updating",
            "Urgent client request",
            "Important system upgrade",
            "Your credentials need renewal",
            "Critical issue reported",
            "Important feedback requested",
            "Your account requires action",
        ]
        for text in important_texts:
            dataset.append((text, "Important"))
        
        # Transactional (50 examples) - Receipts, confirmations
        transactional_texts = [
            "Your Amazon order has been shipped",
            "Bank statement for January 2024",
            "Payment receipt for Rs 5000",
            "Order confirmation #12345",
            "Your transaction was successful",
            "Invoice attached for your purchase",
            "Delivery scheduled for tomorrow",
            "Your payment has been processed",
            "Account statement ready to download",
            "Order delivered successfully",
            "Transaction alert: Rs 2500 debited",
            "Your refund has been initiated",
            "Payment confirmation from Flipkart",
            "Your booking is confirmed",
            "Receipt for your recent purchase",
            "Order tracking number: ABC123",
            "Your subscription has been renewed",
            "Payment successful for Netflix",
            "Your ticket has been booked",
            "Transaction completed successfully",
            "Your order is out for delivery",
            "Bank transfer confirmation",
            "Your payment is being processed",
            "Order status: Shipped",
            "Your purchase receipt",
            "Transaction ID: 123456789",
            "Your booking confirmation",
            "Payment received successfully",
            "Your order has been placed",
            "Delivery confirmation",
            "Your transaction receipt",
            "Order invoice attached",
            "Payment processed for order",
            "Your subscription receipt",
            "Transaction successful notification",
            "Your booking details",
            "Order shipment notification",
            "Payment confirmation email",
            "Your purchase summary",
            "Transaction completed",
            "Your order receipt",
            "Booking confirmation number",
            "Payment acknowledgment",
            "Your transaction details",
            "Order delivery update",
            "Payment success notification",
            "Your purchase confirmation",
            "Transaction record",
            "Order fulfillment notice",
            "Payment verification",
        ]
        for text in transactional_texts:
            dataset.append((text, "Transactional"))
        
        # Promotional (50 examples) - Marketing, sales
        promotional_texts = [
            "50% off sale ends tonight",
            "Limited time offer just for you",
            "Flash sale starting now",
            "Exclusive discount code inside",
            "Don't miss our biggest sale",
            "Special offer: Buy 1 Get 1 Free",
            "Clearance sale up to 70% off",
            "Subscribe and save 30%",
            "Weekend sale is live",
            "Get 25% off your first order",
            "Limited stock available",
            "Mega sale this weekend",
            "Exclusive member discount",
            "Shop now and save big",
            "Special promotion for you",
            "Last chance to save",
            "Hot deals this week",
            "Seasonal sale now on",
            "Upgrade and save 40%",
            "Free shipping on all orders",
            "Black Friday deals",
            "Cyber Monday sale",
            "New year special offers",
            "Summer sale is here",
            "Festive discount inside",
            "Premium membership offer",
            "Limited time deal",
            "Special price for you",
            "Exclusive online sale",
            "Best prices guaranteed",
            "Clearance event today",
            "Flash deal alert",
            "Member exclusive sale",
            "Save up to 60% off",
            "Special bundle offer",
            "Early bird discount",
            "VIP sale access",
            "Promotional code inside",
            "Limited edition sale",
            "Special launch offer",
            "Discount expires soon",
            "Exclusive preview sale",
            "Special rewards offer",
            "Premium upgrade deal",
            "Seasonal promotion",
            "Special event sale",
            "Limited quantity offer",
            "Exclusive partner deal",
            "Special anniversary sale",
            "Promotional campaign",
        ]
        for text in promotional_texts:
            dataset.append((text, "Promotional"))
        
        # Social (50 examples) - Social notifications
        social_texts = [
            "John Doe wants to connect on LinkedIn",
            "Someone commented on your post",
            "New follower on Instagram",
            "You have a new message on Facebook",
            "Someone liked your photo",
            "New connection request",
            "Your friend shared a post",
            "Someone mentioned you in a comment",
            "New activity on your profile",
            "Friend request from Jane",
            "Someone tagged you in a photo",
            "New message in your inbox",
            "Your post got 50 likes",
            "Someone shared your content",
            "New follower notification",
            "Comment on your LinkedIn post",
            "Someone viewed your profile",
            "New connection on Twitter",
            "Your friend posted an update",
            "Someone reacted to your story",
            "New message from colleague",
            "Friend suggestion for you",
            "Someone endorsed your skills",
            "New group invitation",
            "Your post was shared",
            "Someone replied to your comment",
            "New follower on Twitter",
            "Profile view notification",
            "Someone sent you a message",
            "New activity in your network",
            "Friend posted a photo",
            "Someone liked your comment",
            "New connection suggestion",
            "Your content was featured",
            "Someone mentioned you",
            "New group message",
            "Profile update from friend",
            "Someone reacted to your post",
            "New follower alert",
            "Your friend is live",
            "Someone commented on photo",
            "New message request",
            "Profile visit notification",
            "Someone shared your link",
            "New network activity",
            "Friend tagged you",
            "Someone liked your story",
            "New social notification",
            "Your post reached milestone",
            "Someone sent friend request",
        ]
        for text in social_texts:
            dataset.append((text, "Social"))
        
        # Spam (50 examples) - Scams, phishing
        spam_texts = [
            "You've won a lottery of $1 million",
            "Claim your prize now",
            "Get rich quick opportunity",
            "Nigerian prince needs your help",
            "Congratulations! You won an iPhone",
            "Click here to claim reward",
            "Your account will be closed",
            "Verify your account immediately",
            "Suspicious activity detected - click link",
            "You have unclaimed money",
            "Free gift card waiting",
            "Urgent: Update payment info",
            "Your package is held - pay fee",
            "Congratulations winner",
            "Claim your inheritance",
            "Work from home - earn thousands",
            "Free vacation package",
            "Your computer has virus",
            "Account suspended - verify now",
            "You've been selected",
            "Claim your refund",
            "Lottery winner notification",
            "Free money opportunity",
            "Your prize is waiting",
            "Urgent security alert",
            "Verify identity immediately",
            "Your account is locked",
            "Claim your bonus",
            "Free iPhone giveaway",
            "You won a contest",
            "Urgent action required",
            "Your package needs payment",
            "Congratulations on winning",
            "Free gift for you",
            "Your account needs verification",
            "Claim your reward now",
            "You've been chosen",
            "Free money waiting",
            "Your prize notification",
            "Urgent verification needed",
            "Account will be deleted",
            "Claim your gift card",
            "You won lottery",
            "Free vacation offer",
            "Your reward is ready",
            "Urgent payment required",
            "Account suspended notice",
            "Claim your prize money",
            "You've won big",
            "Free offer inside",
        ]
        for text in spam_texts:
            dataset.append((text, "Spam"))
        
        # Separate into texts and labels
        texts = [item[0] for item in dataset]
        labels = [item[1] for item in dataset]
        
        # CRITICAL VALIDATION
        assert len(texts) == len(labels), f"Dataset mismatch: {len(texts)} texts vs {len(labels)} labels"
        
        print(f"Generated synthetic intent dataset: {len(texts)} samples, {len(set(labels))} categories")
        
        return texts, labels
        # Build dataset with explicit pairing to prevent mismatches
        dataset = []
        
        # Banking/Financial (40 examples)
        banking_texts = [
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
        ]
        for text in banking_texts:
            dataset.append((text, "Banking/Financial"))
        
        # Shopping/Orders (40 examples)
        shopping_texts = [
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
        ]
        for text in shopping_texts:
            dataset.append((text, "Shopping/Orders"))
        
        # Work/Career (40 examples)
        work_texts = [
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
        ]
        for text in work_texts:
            dataset.append((text, "Work/Career"))
        
        # Promotional (40 examples)
        promo_texts = [
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
        ]
        for text in promo_texts:
            dataset.append((text, "Promotional"))
        
        # Personal/Other (40 examples)
        personal_texts = [
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
        for text in personal_texts:
            dataset.append((text, "Personal/Other"))
        
        # Separate into texts and labels
        texts = [item[0] for item in dataset]
        labels = [item[1] for item in dataset]
        
        # CRITICAL VALIDATION: Ensure equal lengths
        assert len(texts) == len(labels), f"Dataset mismatch: {len(texts)} texts vs {len(labels)} labels"
        
        print(f"Generated training dataset: {len(texts)} samples, {len(set(labels))} categories")
        
        return texts, labels


# Global instance
_tfidf_classifier = None


def get_tfidf_classifier() -> TFIDFClassifier:
    """Get the global TF-IDF classifier instance."""
    global _tfidf_classifier
    if _tfidf_classifier is None:
        _tfidf_classifier = TFIDFClassifier()
    return _tfidf_classifier
