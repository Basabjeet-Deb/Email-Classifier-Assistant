"""
System metrics tracker for monitoring classification performance.
"""
import time
from typing import Dict, Any
from collections import defaultdict, Counter


class MetricsTracker:
    """
    Track classification metrics and system performance.
    """
    
    def __init__(self):
        """Initialize metrics tracker."""
        self.reset()
    
    def reset(self):
        """Reset all metrics."""
        self.emails_processed = 0
        self.confidences = []
        self.classifier_usage = Counter()
        self.category_counts = Counter()
        self.processing_times = []
        self.start_time = time.time()
    
    def record_classification(self, category: str, confidence: float, 
                            classifier_used: str, processing_time_ms: float):
        """
        Record a classification event.
        
        Args:
            category: Predicted category
            confidence: Confidence score
            classifier_used: Name of classifier
            processing_time_ms: Processing time in milliseconds
        """
        self.emails_processed += 1
        self.confidences.append(confidence)
        self.classifier_usage[classifier_used] += 1
        self.category_counts[category] += 1
        self.processing_times.append(processing_time_ms)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics summary.
        
        Returns:
            Dictionary of metrics
        """
        avg_confidence = (
            sum(self.confidences) / len(self.confidences)
            if self.confidences else 0.0
        )
        
        avg_processing_time = (
            sum(self.processing_times) / len(self.processing_times)
            if self.processing_times else 0.0
        )
        
        uptime_seconds = time.time() - self.start_time
        
        return {
            'emails_processed': self.emails_processed,
            'average_confidence': round(avg_confidence, 3),
            'classifier_usage': dict(self.classifier_usage),
            'category_distribution': dict(self.category_counts),
            'average_processing_time_ms': round(avg_processing_time, 2),
            'uptime_seconds': round(uptime_seconds, 2),
            'transformer_calls': self.classifier_usage.get('zero-shot', 0),
            'tfidf_calls': self.classifier_usage.get('tfidf', 0),
            'keyword_calls': self.classifier_usage.get('keyword', 0),
        }
    
    def get_category_stats(self) -> Dict[str, int]:
        """
        Get category distribution statistics.
        
        Returns:
            Dictionary mapping categories to counts
        """
        return dict(self.category_counts)


# Global metrics tracker
_metrics_tracker = MetricsTracker()


def get_metrics_tracker() -> MetricsTracker:
    """Get the global metrics tracker instance."""
    return _metrics_tracker
