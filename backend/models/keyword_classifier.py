"""
Rule-based keyword classifier for fast, high-confidence predictions.
"""
from typing import Tuple, List, Dict
from backend.config import CATEGORIES


class KeywordClassifier:
    """
    Fast rule-based classifier using keyword matching and domain recognition.
    Provides high-confidence predictions for obvious cases.
    """
    
    def __init__(self):
        """Initialize keyword sets and domain mappings."""
        self.banking_keywords = [
            'account statement', 'transaction', 'balance', 'credit card', 'debit card',
            'payment', 'netbanking', 'upi', 'neft', 'rtgs', 'imps',
            'account alert', 'credited', 'debited', 'withdrawal', 'deposit',
            'statement for', 'minimum balance', 'overdraft', 'loan', 'emi', 'interest',
            'bank account', 'savings account', 'current account', 'fixed deposit',
            'mutual fund', 'investment', 'cheque', 'atm', 'card blocked', 'otp'
        ]
        
        self.banking_domains = [
            'bank', 'sbi', 'hdfc', 'icici', 'axis', 'kotak', 'paytm', 
            'phonepe', 'gpay', 'citi', 'hsbc', 'pnb', 'canara', 'idbi'
        ]
        
        self.shopping_keywords = [
            'order confirmation', 'receipt', 'invoice', 'shipped', 'delivery',
            'tracking', 'your order', 'purchase', 'payment successful', 'order placed',
            'dispatched', 'out for delivery', 'delivered', 'order #', 'order number',
            'thank you for your order', 'shipment', 'package', 'courier', 'tracking number',
            'order has been', 'order status', 'order update', 'estimated delivery'
        ]
        
        self.shopping_domains = [
            'amazon', 'flipkart', 'myntra', 'swiggy', 'zomato', 'uber', 
            'ola', 'ebay', 'shopify', 'meesho', 'ajio', 'nykaa'
        ]
        
        self.work_keywords = [
            'meeting scheduled', 'interview invitation', 'job application', 'resume shortlisted',
            'position available', 'hiring for', 'recruitment process', 'linkedin connection',
            'project deadline', 'task assigned', 'team meeting', 'colleague request',
            'conference call', 'job alert', 'job opening', 'candidate profile'
        ]
        
        self.work_domains = [
            'linkedin', 'naukri', 'indeed', 'glassdoor', 'angellist', 'internshala'
        ]
        
        self.promotional_keywords = [
            'special offer', 'discount', 'sale ends', 'limited time', 'offer expires',
            'buy now', 'shop now', 'deal of', 'save up to', 'free trial', 'subscribe now',
            'exclusive offer', 'promotional', 'advertisement', '% off', 'claim your',
            'dont miss', "don't miss", 'last chance', 'hurry up', 'act now', 'limited offer',
            'flash sale', 'clearance sale', 'mega sale', 'biggest sale', 'promo code',
            'limited stock', 'while supplies last', 'today only', 'ends soon', 'ends today'
        ]
        
        self.personal_domains = [
            'soundcloud', 'spotify', 'youtube', 'perplexity', 'adobe', 'medium',
            'substack', 'honeygain', 'facebook', 'twitter', 'instagram',
            'coursera', 'udemy', 'edx', 'claude', 'canva', 'notion', 'figma'
        ]
        
        self.personal_keywords = [
            'newsletter from', 'weekly digest', 'monthly update', 'whats new in', "what's new in",
            'new feature', 'product update', 'introducing our', 'update from',
            'learn from', 'learn about', 'educational content', 'online course'
        ]
    
    def classify(self, subject: str, sender: str, body_snippet: str, 
                 sender_domain: str) -> Tuple[str, float, List[str]]:
        """
        Classify email using keyword matching.
        
        Args:
            subject: Email subject
            sender: Email sender
            body_snippet: Email body preview
            sender_domain: Extracted sender domain
            
        Returns:
            Tuple of (category, confidence, matched_keywords) or (None, 0.0, [])
        """
        combined_text = f"{subject} {body_snippet}".lower()
        sender_lower = sender.lower()
        
        # Check personal/content platform domains first
        has_personal_domain = any(domain in sender_domain for domain in self.personal_domains)
        if has_personal_domain:
            promo_matches = [kw for kw in self.promotional_keywords if kw in combined_text]
            if promo_matches and len(promo_matches) >= 2:
                return "Promotional", 0.90, promo_matches
            else:
                return "Personal/Other", 0.92, []
        
        # Banking/Financial (highest priority)
        banking_matches = [kw for kw in self.banking_keywords if kw in combined_text]
        has_banking_domain = any(domain in sender_domain for domain in self.banking_domains)
        if banking_matches or has_banking_domain:
            confidence = 0.98 if (banking_matches and has_banking_domain) else 0.92 if banking_matches else 0.88
            return "Banking/Financial", confidence, banking_matches
        
        # Shopping/Orders
        shopping_matches = [kw for kw in self.shopping_keywords if kw in combined_text]
        has_shopping_domain = any(domain in sender_domain for domain in self.shopping_domains)
        if shopping_matches or has_shopping_domain:
            confidence = 0.96 if (shopping_matches and has_shopping_domain) else 0.90 if shopping_matches else 0.85
            return "Shopping/Orders", confidence, shopping_matches
        
        # Work/Career
        work_matches = [kw for kw in self.work_keywords if kw in combined_text]
        has_work_domain = any(domain in sender_domain for domain in self.work_domains)
        if work_matches or has_work_domain:
            confidence = 0.94 if (work_matches and has_work_domain) else 0.88 if work_matches else 0.82
            return "Work/Career", confidence, work_matches
        
        # Promotional
        promo_matches = [kw for kw in self.promotional_keywords if kw in combined_text]
        if promo_matches:
            return "Promotional", 0.91, promo_matches
        
        # Personal/Other
        personal_matches = [kw for kw in self.personal_keywords if kw in combined_text]
        if personal_matches:
            return "Personal/Other", 0.85, personal_matches
        
        # No match
        return None, 0.0, []
