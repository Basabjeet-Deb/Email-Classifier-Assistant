"""
Classification service orchestrating the multi-stage classification pipeline.
"""
import time
from typing import Tuple, Dict, Any

from backend.models.keyword_classifier import KeywordClassifier
from backend.models.tfidf_classifier_robust import get_robust_tfidf_classifier
from backend.models.zero_shot_classifier import get_zero_shot_classifier
from backend.utils.email_processor import extract_email_features
from backend.caching.lru_cache import get_cache
from backend.metrics.tracker import get_metrics_tracker


class ClassificationService:
    """
    Multi-stage classification pipeline with memory optimization.
    
    Pipeline:
    1. Check cache
    2. Keyword classifier (fast, high confidence)
    3. TF-IDF classifier (accurate, low memory)
    4. Zero-shot classifier (fallback, high memory - disabled by default)
    """
    
    def __init__(self):
        """Initialize the classification service."""
        self.keyword_classifier = KeywordClassifier()
        self.tfidf_classifier = get_robust_tfidf_classifier()
        self.zero_shot_classifier = get_zero_shot_classifier()
        self.cache = get_cache()
        self.metrics = get_metrics_tracker()
        
        # Confidence thresholds
        self.keyword_threshold = 0.85  # Use keyword for strong matches
        self.tfidf_threshold = 0.40  # Use TF-IDF for most cases
        self.hybrid_mode = True  # Enable hybrid classification
    
    def classify_email(self, subject: str, sender: str, body_snippet: str) -> Dict[str, Any]:
        """
        Classify an email using TF-IDF as primary with keyword confidence boosting.
        
        Args:
            subject: Email subject
            sender: Email sender
            body_snippet: Email body preview
            
        Returns:
            Classification result dictionary
        """
        start_time = time.time()
        
        # Step 1: Check cache
        cached_result = self.cache.get(subject, sender, body_snippet)
        if cached_result:
            category, confidence, classifier_used = cached_result
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Record metrics
            self.metrics.record_classification(
                category, confidence, f"{classifier_used} (cached)", processing_time_ms
            )
            
            return {
                'category': category,
                'confidence': confidence,
                'classifier_used': f"{classifier_used} (cached)",
                'processing_time_ms': round(processing_time_ms, 2),
                'from_cache': True
            }
        
        # Extract features
        features = extract_email_features(subject, sender, body_snippet)
        sender_domain = features['sender_domain']
        
        # Step 2: Get TF-IDF prediction (PRIMARY - Robust model)
        tfidf_category, tfidf_confidence, all_scores = self.tfidf_classifier.classify(
            sender, subject, body_snippet
        )
        
        # Step 3: Get keyword prediction for validation/boosting
        keyword_category, keyword_confidence, matched_keywords = self.keyword_classifier.classify(
            subject, sender, body_snippet, sender_domain
        )
        
        # Step 4: Decision Logic - TF-IDF primary with keyword boosting
        processing_time_ms = (time.time() - start_time) * 1000
        
        # If both agree and both are confident, boost confidence
        if (keyword_category == tfidf_category and 
            keyword_confidence >= 0.85 and 
            tfidf_confidence >= 0.75):
            # Boost confidence when both agree
            final_confidence = min(tfidf_confidence + 0.08, 0.99)
            classifier_used = 'tfidf+keyword'
            
            self.cache.set(subject, sender, body_snippet, tfidf_category, final_confidence, classifier_used)
            self.metrics.record_classification(
                tfidf_category, final_confidence, classifier_used, processing_time_ms
            )
            
            return {
                'category': tfidf_category,
                'confidence': final_confidence,
                'classifier_used': classifier_used,
                'processing_time_ms': round(processing_time_ms, 2),
                'matched_keywords': matched_keywords[:5],
                'all_scores': all_scores,
                'agreement': True,
                'from_cache': False
            }
        
        # Otherwise, use TF-IDF result (most accurate)
        classifier_used = 'tfidf'
        
        self.cache.set(subject, sender, body_snippet, tfidf_category, tfidf_confidence, classifier_used)
        self.metrics.record_classification(
            tfidf_category, tfidf_confidence, classifier_used, processing_time_ms
        )
        
        return {
            'category': tfidf_category,
            'confidence': tfidf_confidence,
            'classifier_used': classifier_used,
            'processing_time_ms': round(processing_time_ms, 2),
            'all_scores': all_scores,
            'keyword_suggestion': keyword_category if keyword_category else None,
            'from_cache': False
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics."""
        metrics = self.metrics.get_metrics()
        cache_stats = self.cache.get_stats()
        
        return {
            **metrics,
            'cache_stats': cache_stats
        }
    
    def get_category_stats(self) -> Dict[str, int]:
        """Get category distribution statistics."""
        return self.metrics.get_category_stats()


# Global service instance
_classification_service = None


def get_classification_service() -> ClassificationService:
    """Get the global classification service instance."""
    global _classification_service
    if _classification_service is None:
        _classification_service = ClassificationService()
    return _classification_service
