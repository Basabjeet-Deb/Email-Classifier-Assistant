"""
Zero-shot transformer classifier wrapper with memory optimization.
Only loaded when explicitly needed to save RAM.
"""
from typing import Tuple, Dict, Optional
from backend.config import ZERO_SHOT_MODEL, USE_ZERO_SHOT, CATEGORIES


class ZeroShotClassifier:
    """
    HuggingFace zero-shot classifier wrapper.
    Memory-intensive (~500MB-1GB), only used as fallback.
    """
    
    def __init__(self):
        """Initialize the classifier (model not loaded yet)."""
        self.model = None
        self.is_loaded = False
        self.enabled = USE_ZERO_SHOT
    
    def load_model(self) -> bool:
        """
        Lazy load the transformer model.
        Only called when needed to save memory.
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        if not self.enabled:
            print("Zero-shot classifier is disabled (memory optimization)")
            return False
        
        if self.is_loaded:
            return True
        
        try:
            from transformers import pipeline
            print(f"Loading zero-shot model: {ZERO_SHOT_MODEL}...")
            print("WARNING: This will consume ~500MB-1GB RAM")
            
            self.model = pipeline(
                "zero-shot-classification",
                model=ZERO_SHOT_MODEL,
                device=-1,  # CPU only
                batch_size=1,  # Minimize memory usage
                max_length=128,
                truncation=True
            )
            
            self.is_loaded = True
            print("Zero-shot model loaded successfully.")
            return True
        except Exception as e:
            print(f"Failed to load zero-shot model: {e}")
            return False
    
    def unload_model(self):
        """
        Unload the model to free memory.
        Call this after classification if memory is constrained.
        """
        if self.is_loaded:
            self.model = None
            self.is_loaded = False
            print("Zero-shot model unloaded to free memory.")
    
    def classify(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        """
        Classify text using zero-shot learning.
        
        Args:
            text: Text to classify
            
        Returns:
            Tuple of (category, confidence, all_scores)
        """
        if not self.enabled:
            return "Personal/Other", 0.5, {}
        
        if not self.is_loaded:
            success = self.load_model()
            if not success:
                return "Personal/Other", 0.5, {}
        
        try:
            # Truncate text to save memory
            text = text[:500]
            
            # Run classification
            result = self.model(text, candidate_labels=CATEGORIES)
            
            # Extract results
            category = result['labels'][0]
            confidence = result['scores'][0]
            all_scores = {label: score for label, score in zip(result['labels'], result['scores'])}
            
            return category, confidence, all_scores
        except Exception as e:
            print(f"Zero-shot classification error: {e}")
            return "Personal/Other", 0.5, {}


# Global instance
_zero_shot_classifier = None


def get_zero_shot_classifier() -> ZeroShotClassifier:
    """Get the global zero-shot classifier instance."""
    global _zero_shot_classifier
    if _zero_shot_classifier is None:
        _zero_shot_classifier = ZeroShotClassifier()
    return _zero_shot_classifier
