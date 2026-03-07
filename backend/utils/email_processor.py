"""
Email preprocessing and feature extraction utilities.
"""
import re
from typing import Dict, Any


def extract_email_features(subject: str, sender: str, body_snippet: str) -> Dict[str, Any]:
    """
    Extract meaningful features from email for classification.
    
    Args:
        subject: Email subject line
        sender: Email sender address
        body_snippet: Email body preview
        
    Returns:
        Dictionary of extracted features
    """
    combined_text = f"{subject} {body_snippet}"
    
    features = {
        'subject_length': len(subject),
        'body_length': len(body_snippet),
        'has_numbers': any(char.isdigit() for char in combined_text),
        'has_currency': any(symbol in combined_text for symbol in ['$', '€', '£', '₹', 'Rs']),
        'has_percentage': '%' in combined_text,
        'has_urgency': any(word in combined_text.lower() for word in ['urgent', 'asap', 'immediately', 'now']),
        'sender_domain': extract_domain(sender),
        'all_caps_ratio': sum(1 for c in subject if c.isupper()) / max(len(subject), 1),
        'exclamation_count': combined_text.count('!'),
        'question_count': combined_text.count('?'),
    }
    
    return features


def extract_domain(sender: str) -> str:
    """Extract domain from email sender address."""
    if '@' in sender:
        return sender.split('@')[-1].split('>')[0].strip().lower()
    return 'unknown'


def preprocess_text(text: str) -> str:
    """
    Clean and normalize text for classification.
    
    Args:
        text: Raw text to preprocess
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-]', '', text)
    
    # Lowercase
    text = text.lower()
    
    return text


def create_classification_text(subject: str, sender: str, body_snippet: str, features: Dict[str, Any]) -> str:
    """
    Create optimized text representation for classification.
    
    Args:
        subject: Email subject
        sender: Email sender
        body_snippet: Email body preview
        features: Extracted features
        
    Returns:
        Formatted text for classification
    """
    sender_domain = features['sender_domain']
    
    # Combine relevant information
    text_parts = [
        subject,
        sender_domain,
        body_snippet[:200]  # Limit body snippet length
    ]
    
    # Add feature signals
    if features['has_currency']:
        text_parts.append('financial transaction')
    if features['has_urgency']:
        text_parts.append('urgent action required')
    
    return ' '.join(filter(None, text_parts))
