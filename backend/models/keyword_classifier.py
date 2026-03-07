"""
Rule-based keyword classifier for fast, high-confidence predictions.
"""
from typing import Tuple, List, Dict
from backend.config import CATEGORIES


class KeywordClassifier:
    """
    Fast rule-based classifier using keyword matching for intent detection.
    Focuses on email importance and purpose rather than topic.
    """
    
    def __init__(self):
        """Initialize keyword sets for intent detection."""
        # Important - Requires immediate attention
        self.important_keywords = [
            'urgent', 'important', 'action required', 'immediate', 'asap',
            'deadline', 'expires', 'expiring', 'interview', 'job offer',
            'security alert', 'account locked', 'suspended', 'verification required',
            'password reset', 'critical', 'emergency', 'attention needed',
            'review required', 'approval needed', 'response needed',
            'meeting scheduled', 'project deadline', 'client meeting',
            'offer letter', 'employment', 'hiring'
        ]
        
        # Transactional - Receipts, confirmations, statements
        self.transactional_keywords = [
            'receipt', 'invoice', 'order confirmation', 'payment successful',
            'transaction', 'statement', 'shipped', 'delivered', 'tracking',
            'booking confirmed', 'reservation', 'ticket', 'confirmation number',
            'order #', 'transaction id', 'payment processed', 'refund',
            'order placed', 'order status', 'delivery update'
        ]
        
        self.transactional_domains = [
            'amazon', 'flipkart', 'myntra', 'swiggy', 'zomato',
            'bank', 'sbi', 'hdfc', 'icici', 'axis', 'paytm'
        ]
        
        # Promotional - Marketing, sales, offers
        self.promotional_keywords = [
            'sale', 'discount', 'offer', 'deal', 'save', 'off',
            'limited time', 'exclusive', 'special', 'promotion',
            'flash sale', 'clearance', 'buy now', 'shop now',
            'subscribe', 'upgrade', 'free trial', 'limited stock',
            'best price', 'hot deal', 'mega sale', 'seasonal'
        ]
        
        # Social - Social network notifications
        self.social_keywords = [
            'commented', 'liked', 'shared', 'tagged', 'mentioned',
            'follower', 'connection request', 'friend request',
            'new message', 'replied', 'reacted', 'viewed your profile',
            'wants to connect', 'endorsed', 'group invitation'
        ]
        
        self.social_domains = [
            'linkedin', 'facebook', 'twitter', 'instagram',
            'reddit', 'quora', 'medium', 'github'
        ]
        
        # Spam - Scams, phishing, suspicious
        self.spam_keywords = [
            'won', 'winner', 'lottery', 'prize', 'claim', 'congratulations',
            'free money', 'get rich', 'inheritance', 'nigerian prince',
            'click here', 'verify account', 'suspended account',
            'urgent verification', 'claim reward', 'you\'ve been selected',
            'free gift card', 'work from home', 'earn thousands',
            'prince needs help', 'nigerian', 'foreign prince'
        ]
    
    def classify(self, subject: str, sender: str, body_snippet: str, 
                 sender_domain: str) -> Tuple[str, float, List[str]]:
        """
        Classify email intent using keyword matching with improved confidence scoring.
        
        Args:
            subject: Email subject
            sender: Email sender
            body_snippet: Email body preview
            sender_domain: Extracted sender domain
            
        Returns:
            Tuple of (category, confidence, matched_keywords) or (None, 0.0, [])
        """
        combined_text = f"{subject} {body_snippet}".lower()
        
        # Priority 1: Check for spam (highest priority for safety)
        spam_matches = [kw for kw in self.spam_keywords if kw in combined_text]
        if len(spam_matches) >= 1:  # Even single strong spam indicator
            # Higher confidence with more matches
            confidence = min(0.90 + len(spam_matches) * 0.02, 0.98)
            return "Spam", confidence, spam_matches
        
        # Priority 2: Check for promotional content (before important to catch marketing)
        promo_matches = [kw for kw in self.promotional_keywords if kw in combined_text]
        # Check if "offer" is in context of job offer (important) vs promotional offer
        has_job_context = any(kw in combined_text for kw in ['job', 'employment', 'hiring', 'career', 'position'])
        
        if len(promo_matches) >= 2 and not has_job_context:  # Need multiple promo indicators
            # Scale confidence with number of matches
            confidence = min(0.85 + (len(promo_matches) - 2) * 0.02, 0.94)
            return "Promotional", confidence, promo_matches
        
        # Priority 3: Check for important/urgent emails
        important_matches = [kw for kw in self.important_keywords if kw in combined_text]
        if important_matches:
            # Scale confidence based on number of matches
            if len(important_matches) >= 3:
                confidence = 0.95
            elif len(important_matches) >= 2:
                confidence = 0.90
            else:
                confidence = 0.85
            return "Important", confidence, important_matches
        
        # Priority 4: Check for transactional emails
        # But skip if promotional keywords are present (e.g., "SBI credit card offer")
        transactional_matches = [kw for kw in self.transactional_keywords if kw in combined_text]
        has_transactional_domain = any(domain in sender_domain for domain in self.transactional_domains)
        
        # Don't classify as transactional if promotional keywords exist
        if (transactional_matches or has_transactional_domain) and len(promo_matches) == 0:
            # Best confidence when both keywords and domain match
            if transactional_matches and has_transactional_domain:
                confidence = min(0.92 + len(transactional_matches) * 0.01, 0.96)
            elif len(transactional_matches) >= 2:
                confidence = 0.88
            elif transactional_matches:
                confidence = 0.85
            else:
                confidence = 0.82
            return "Transactional", confidence, transactional_matches
        
        # Priority 5: Check for social notifications
        social_matches = [kw for kw in self.social_keywords if kw in combined_text]
        has_social_domain = any(domain in sender_domain for domain in self.social_domains)
        
        if social_matches or has_social_domain:
            # Best confidence when both keywords and domain match
            if social_matches and has_social_domain:
                confidence = min(0.90 + len(social_matches) * 0.01, 0.95)
            elif len(social_matches) >= 2:
                confidence = 0.86
            elif social_matches:
                confidence = 0.83
            else:
                confidence = 0.80
            return "Social", confidence, social_matches
        
        # No match
        return None, 0.0, []
