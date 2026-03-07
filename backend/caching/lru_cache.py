"""
LRU Cache implementation for classification results.
"""
import hashlib
import time
from collections import OrderedDict
from typing import Optional, Tuple, Any
from backend.config import CACHE_MAX_SIZE, CACHE_TTL


class ClassificationCache:
    """
    LRU Cache for storing classification results.
    Reduces redundant model inference for similar emails.
    """
    
    def __init__(self, max_size: int = CACHE_MAX_SIZE, ttl: int = CACHE_TTL):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of entries to store
            ttl: Time-to-live for cache entries in seconds
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, subject: str, sender: str, body_snippet: str) -> str:
        """Generate a unique cache key from email content."""
        content = f"{subject}|{sender}|{body_snippet[:100]}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, subject: str, sender: str, body_snippet: str) -> Optional[Tuple[str, float, str]]:
        """
        Retrieve cached classification result.
        
        Args:
            subject: Email subject
            sender: Email sender
            body_snippet: Email body preview
            
        Returns:
            Tuple of (category, confidence, classifier_used) or None if not cached
        """
        key = self._generate_key(subject, sender, body_snippet)
        
        if key in self.cache:
            entry = self.cache[key]
            timestamp, result = entry
            
            # Check if entry is still valid
            if time.time() - timestamp < self.ttl:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                self.hits += 1
                return result
            else:
                # Entry expired, remove it
                del self.cache[key]
        
        self.misses += 1
        return None
    
    def set(self, subject: str, sender: str, body_snippet: str, 
            category: str, confidence: float, classifier_used: str):
        """
        Store classification result in cache.
        
        Args:
            subject: Email subject
            sender: Email sender
            body_snippet: Email body preview
            category: Predicted category
            confidence: Confidence score
            classifier_used: Name of classifier that made the prediction
        """
        key = self._generate_key(subject, sender, body_snippet)
        
        # Remove oldest entry if cache is full
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        
        # Store with timestamp
        self.cache[key] = (time.time(), (category, confidence, classifier_used))
    
    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 2),
            'total_requests': total_requests
        }


# Global cache instance
_classification_cache = ClassificationCache()


def get_cache() -> ClassificationCache:
    """Get the global classification cache instance."""
    return _classification_cache
