"""
Robust TF-IDF classifier that handles real-world email noise.
Uses aggressive preprocessing and dual vectorizers (word + char ngrams).
"""
import joblib
import numpy as np
from pathlib import Path
from typing import Tuple, Dict
from scipy.sparse import hstack

from backend.config import MODELS_DIR
from backend.utils.robust_preprocessor import RobustEmailPreprocessor

MODEL_PATH = MODELS_DIR / "tfidf_classifier.pkl"


class RobustTFIDFClassifier:
    """
    Robust TF-IDF email classifier with aggressive preprocessing.
    Designed to handle real-world email noise and generalize better.
    """
    
    def __init__(self):
        """Initialize the robust classifier."""
        self.model = None
        self.word_vectorizer = None
        self.char_vectorizer = None
        self.preprocessor = None
        self.classes = None
        self.is_loaded = False
    
    def load_model(self) -> bool:
        """Load the trained robust model."""
        if not MODEL_PATH.exists():
            print(f"Model not found at {MODEL_PATH}")
            return False
        
        try:
            print(f"Loading robust TF-IDF model from {MODEL_PATH}...")
            model_data = joblib.load(MODEL_PATH)
            
            self.model = model_data['model']
            self.word_vectorizer = model_data['word_vectorizer']
            self.char_vectorizer = model_data['char_vectorizer']
            self.preprocessor = model_data['preprocessor']
            self.classes = model_data['classes']
            
            self.is_loaded = True
            print(f"✓ Robust TF-IDF model loaded successfully. Classes: {len(self.classes)}")
            return True
            
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def classify(self, sender: str, subject: str, body: str) -> Tuple[str, float, Dict[str, float]]:
        """
        Classify an email using the robust model.
        
        Args:
            sender: Email sender
            subject: Email subject
            body: Email body
            
        Returns:
            Tuple of (category, confidence, all_scores)
        """
        # Lazy load model
        if not self.is_loaded:
            if not self.load_model():
                return "Unknown", 0.0, {}
        
        try:
            # Create robust text using preprocessor
            robust_text = self.preprocessor.create_robust_text(sender, subject, body)
            
            # Transform using both vectorizers
            text_word = self.word_vectorizer.transform([robust_text])
            text_char = self.char_vectorizer.transform([robust_text])
            text_combined = hstack([text_word, text_char])
            
            # Predict
            probabilities = self.model.predict_proba(text_combined)[0]
            predicted_idx = np.argmax(probabilities)
            category = self.classes[predicted_idx]
            confidence = probabilities[predicted_idx]
            
            # Apply confidence calibration for real-world emails
            # Model is trained on clean data, real emails need boost
            sorted_probs = sorted(probabilities, reverse=True)
            if len(sorted_probs) >= 2:
                top_prob = sorted_probs[0]
                second_prob = sorted_probs[1]
                margin = top_prob - second_prob
                
                # If there's a clear winner, boost confidence
                if margin >= 0.25:  # 25%+ margin
                    confidence = min(confidence * 1.35, 0.95)  # 35% boost
                elif margin >= 0.15:  # 15-25% margin
                    confidence = min(confidence * 1.25, 0.90)  # 25% boost
                elif margin >= 0.10:  # 10-15% margin
                    confidence = min(confidence * 1.15, 0.85)  # 15% boost
                else:
                    confidence = min(confidence * 1.05, 0.80)  # 5% boost
            
            # Create scores dictionary
            all_scores = {
                class_name: float(prob)
                for class_name, prob in zip(self.classes, probabilities)
            }
            
            return category, confidence, all_scores
            
        except Exception as e:
            print(f"Classification error: {e}")
            return "Unknown", 0.0, {}


# Global instance
_robust_classifier = None


def get_robust_tfidf_classifier() -> RobustTFIDFClassifier:
    """Get the global robust TF-IDF classifier instance."""
    global _robust_classifier
    if _robust_classifier is None:
        _robust_classifier = RobustTFIDFClassifier()
    return _robust_classifier
