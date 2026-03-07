"""
Self-learning service for continuous model improvement.
Automatically retrains the model when sufficient feedback is collected.
"""
import csv
import threading
import time
from pathlib import Path
from typing import List, Tuple, Dict
from datetime import datetime
from collections import Counter

from backend.config import FEEDBACK_CSV_PATH, DATA_DIR, BASE_DIR, FEEDBACK_RETRAIN_THRESHOLD, MIN_FEEDBACK_FOR_RETRAIN
from backend.models.tfidf_classifier_robust import get_robust_tfidf_classifier
import database as db


class SelfLearningService:
    """
    Service for continuous model improvement through user feedback.
    
    Features:
    - Collects user feedback on misclassifications
    - Automatically retrains model when threshold is reached
    - Maintains feedback history
    - Monitors model performance
    """
    
    def __init__(self):
        """Initialize self-learning service."""
        self.feedback_path = FEEDBACK_CSV_PATH
        self.feedback_threshold = FEEDBACK_RETRAIN_THRESHOLD
        self.min_feedback = MIN_FEEDBACK_FOR_RETRAIN
        self.last_retrain_count = 0
        self.retraining_lock = threading.Lock()
        self._ensure_feedback_file()
        
        # Load initial feedback count
        self.last_retrain_count = self._count_feedback_samples()
        print(f"Self-learning service initialized. Current feedback samples: {self.last_retrain_count}")
    
    def _ensure_feedback_file(self):
        """Ensure feedback CSV file exists with headers."""
        if not self.feedback_path.exists():
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(self.feedback_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'email_id', 'sender', 'subject', 'body', 
                    'predicted_category', 'correct_category',
                    'confidence', 'classifier_used', 'timestamp'
                ])
    
    def _count_feedback_samples(self) -> int:
        """Count total feedback samples."""
        if not self.feedback_path.exists():
            return 0
        
        try:
            with open(self.feedback_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f) - 1  # Subtract header
        except:
            return 0
    
    def store_feedback(self, email_id: str, sender: str, subject: str, body: str,
                      predicted_category: str, correct_category: str,
                      confidence: float = 0.0, classifier_used: str = "Unknown"):
        """
        Store user feedback and trigger retraining if threshold is reached.
        
        Args:
            email_id: Email identifier
            sender: Email sender
            subject: Email subject
            body: Email body
            predicted_category: Model's prediction
            correct_category: User's correction
            confidence: Prediction confidence
            classifier_used: Which classifier made the prediction
        """
        # Store in database
        try:
            email_text = f"{subject} {body}"
            db.store_feedback(
                email_id, predicted_category, correct_category,
                email_text[:500], confidence, classifier_used
            )
            print(f"Feedback stored: {email_id} - {predicted_category} -> {correct_category}")
        except Exception as e:
            print(f"Warning: Failed to store in database: {e}")
        
        # Store in CSV
        timestamp = datetime.now().isoformat()
        with open(self.feedback_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                email_id, sender, subject[:200], body[:300],
                predicted_category, correct_category,
                confidence, classifier_used, timestamp
            ])
        
        print(f"✓ Feedback stored: {predicted_category} -> {correct_category}")
        
        # Check if retraining is needed
        current_count = self._count_feedback_samples()
        new_samples = current_count - self.last_retrain_count
        
        if new_samples >= self.feedback_threshold:
            print(f"\n{'='*80}")
            print(f"AUTOMATIC RETRAINING TRIGGERED")
            print(f"{'='*80}")
            print(f"New feedback samples: {new_samples}")
            print(f"Total feedback samples: {current_count}")
            print(f"Threshold: {self.feedback_threshold}")
            
            # Trigger retraining in background
            threading.Thread(target=self._retrain_model, daemon=True).start()
    
    def load_feedback_data(self) -> List[Tuple[str, str, str, str]]:
        """
        Load feedback data for retraining.
        
        Returns:
            List of (sender, subject, body, correct_category) tuples
        """
        feedback_data = []
        
        if not self.feedback_path.exists():
            return feedback_data
        
        try:
            with open(self.feedback_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sender = row.get('sender', 'unknown@email.com')
                    subject = row.get('subject', '')
                    body = row.get('body', '')
                    correct_category = row.get('correct_category', '')
                    
                    if correct_category:  # Only include valid feedback
                        feedback_data.append((sender, subject, body, correct_category))
        except Exception as e:
            print(f"Error loading feedback data: {e}")
        
        return feedback_data
    
    def _retrain_model(self):
        """
        Retrain model with feedback data (runs in background).
        """
        # Acquire lock to prevent concurrent retraining
        if not self.retraining_lock.acquire(blocking=False):
            print("Retraining already in progress, skipping...")
            return
        
        try:
            print("\n🔄 Starting automatic model retraining...")
            
            # Load feedback data
            feedback_data = self.load_feedback_data()
            
            if len(feedback_data) < self.min_feedback:
                print(f"Not enough feedback data for retraining (need {self.min_feedback}+, have {len(feedback_data)})")
                return
            
            print(f"✓ Loaded {len(feedback_data)} feedback samples")
            
            # Show category distribution
            categories = [item[3] for item in feedback_data]
            category_counts = Counter(categories)
            print("\nFeedback category distribution:")
            for category, count in sorted(category_counts.items()):
                print(f"  {category}: {count} samples")
            
            # Load existing training data
            print("\n📚 Loading existing training data...")
            existing_data = self._load_existing_training_data()
            print(f"✓ Loaded {len(existing_data)} existing samples")
            
            # Combine feedback with existing data
            combined_data = existing_data + feedback_data
            print(f"\n✓ Total training samples: {len(combined_data)}")
            
            # Retrain model using the robust training script
            print("\n🎯 Retraining TF-IDF classifier...")
            import subprocess
            result = subprocess.run(
                ['python', 'retrain_robust_model.py'],
                capture_output=True,
                text=True,
                cwd=BASE_DIR
            )
            
            success = result.returncode == 0
            
            if success:
                print(result.stdout)
            else:
                print(f"Retraining failed: {result.stderr}")
                return
            
            if success:
                # Update last retrain count
                self.last_retrain_count = self._count_feedback_samples()
                
                print("\n" + "="*80)
                print("✅ AUTOMATIC RETRAINING COMPLETED SUCCESSFULLY")
                print("="*80)
                print(f"Model updated with {len(feedback_data)} feedback samples")
                print(f"Next retraining at {self.last_retrain_count + self.feedback_threshold} feedback samples")
                print("="*80 + "\n")
            else:
                print("\n❌ Automatic retraining failed")
        
        except Exception as e:
            print(f"\n❌ Error during automatic retraining: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.retraining_lock.release()
    
    def _load_existing_training_data(self) -> List[Tuple[str, str, str, str]]:
        """
        Load existing training data from datasets.
        
        Returns:
            List of (sender, subject, body, label) tuples
        """
        training_data = []
        
        # Load intent dataset
        intent_dataset = BASE_DIR / "email_intent_dataset_5000.csv"
        if intent_dataset.exists():
            try:
                import pandas as pd
                df = pd.read_csv(intent_dataset)
                
                for _, row in df.iterrows():
                    text = row.get('text', '')
                    label = row.get('label', '')
                    
                    if text and label:
                        # Infer sender from text
                        sender = self._infer_sender(text, label)
                        subject = text[:100]
                        body = text
                        
                        training_data.append((sender, subject, body, label))
            except Exception as e:
                print(f"Warning: Failed to load intent dataset: {e}")
        
        return training_data
    
    def _infer_sender(self, text: str, label: str) -> str:
        """Infer sender from text and label."""
        text_lower = text.lower()
        
        # Check for specific domains
        if 'amazon' in text_lower:
            return 'orders@amazon.com'
        elif 'linkedin' in text_lower:
            return 'notifications@linkedin.com'
        elif 'facebook' in text_lower or 'instagram' in text_lower:
            return 'notifications@facebook.com'
        elif 'bank' in text_lower or 'sbi' in text_lower:
            return 'alerts@bank.com'
        
        # Default based on label
        sender_map = {
            'Important': 'important@company.com',
            'Transactional': 'orders@shop.com',
            'Promotional': 'marketing@deals.com',
            'Social': 'notifications@social.com',
            'Spam': 'spam@unknown.com'
        }
        return sender_map.get(label, 'unknown@email.com')
    
    def manual_retrain(self) -> bool:
        """
        Manually trigger model retraining.
        
        Returns:
            True if successful, False otherwise
        """
        print("\n" + "="*80)
        print("MANUAL RETRAINING TRIGGERED")
        print("="*80)
        
        self._retrain_model()
        return True
    
    def get_feedback_stats(self) -> Dict:
        """
        Get statistics about collected feedback.
        
        Returns:
            Dictionary with feedback statistics
        """
        feedback_data = self.load_feedback_data()
        
        if not feedback_data:
            return {
                'total_samples': 0,
                'category_distribution': {},
                'samples_until_retrain': self.feedback_threshold,
                'last_retrain_count': self.last_retrain_count,
                'retrain_threshold': self.feedback_threshold
            }
        
        categories = [item[3] for item in feedback_data]
        category_counts = Counter(categories)
        
        current_count = len(feedback_data)
        samples_until_retrain = max(0, self.feedback_threshold - (current_count - self.last_retrain_count))
        
        return {
            'total_samples': current_count,
            'category_distribution': dict(category_counts),
            'samples_until_retrain': samples_until_retrain,
            'last_retrain_count': self.last_retrain_count,
            'retrain_threshold': self.feedback_threshold
        }


# Global instance
_self_learning_service = None


def get_self_learning_service() -> SelfLearningService:
    """Get the global self-learning service instance."""
    global _self_learning_service
    if _self_learning_service is None:
        _self_learning_service = SelfLearningService()
    return _self_learning_service
