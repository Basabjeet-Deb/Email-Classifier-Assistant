"""
Robust email preprocessor for handling real-world email noise.
"""
import re


class RobustEmailPreprocessor:
    """Aggressive email cleaning for real-world robustness."""
    
    def __init__(self):
        # Noise patterns to remove
        self.noise_patterns = [
            r'<[^>]+>',  # HTML tags
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # URLs
            r'unsubscribe',
            r'view in browser',
            r'click here',
            r'privacy policy',
            r'terms of service',
            r'reply above this line',
            r'forwarded message',
            r'original message',
            r'from:.*sent:',
            r'-----.*-----',
            r'________________________________',
            r'&[a-z]+;',  # HTML entities
            r'\[image:.*?\]',
            r'©.*?all rights reserved',
        ]
        
    def clean_text(self, text: str) -> str:
        """Aggressively clean email text."""
        if not text:
            return ""
        
        text = text.lower()
        
        # Remove noise patterns
        for pattern in self.noise_patterns:
            text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_features(self, subject: str, body: str) -> dict:
        """Extract structured features from email."""
        combined = f"{subject} {body}".lower()
        
        features = {
            'has_link': 'http' in combined or 'www.' in combined,
            'has_price': bool(re.search(r'[$€£¥]\s*\d+|price|cost|\d+\s*(?:dollar|euro|pound)', combined)),
            'has_date': bool(re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}', combined)),
            'many_exclamation': combined.count('!') >= 2,
            'numeric_heavy': len(re.findall(r'\d+', combined)) >= 3,
            'uppercase_words': len(re.findall(r'\b[A-Z]{2,}\b', subject + body)) >= 2,
            'has_discount': bool(re.search(r'discount|sale|off|deal|save', combined)),
            'has_urgent': bool(re.search(r'urgent|important|asap|immediate|action required', combined)),
        }
        
        return features
    
    def create_feature_tokens(self, features: dict) -> str:
        """Convert features to tokens."""
        tokens = []
        if features['has_link']:
            tokens.append('HAS_LINK')
        if features['has_price']:
            tokens.append('HAS_PRICE')
        if features['has_date']:
            tokens.append('HAS_DATE')
        if features['many_exclamation']:
            tokens.append('MANY_EXCLAMATION')
        if features['numeric_heavy']:
            tokens.append('NUMERIC_HEAVY')
        if features['uppercase_words']:
            tokens.append('HAS_UPPERCASE')
        if features['has_discount']:
            tokens.append('HAS_DISCOUNT')
        if features['has_urgent']:
            tokens.append('HAS_URGENT')
        
        return ' '.join(tokens)
    
    def extract_domain(self, sender: str) -> str:
        """Extract and normalize domain."""
        if not sender or '@' not in sender:
            return 'DOMAIN_UNKNOWN'
        
        domain = sender.split('@')[-1].lower()
        domain = domain.split('.')[0]  # Get main part
        
        # Normalize common domains
        domain_map = {
            'amazon': 'DOMAIN_AMAZON',
            'linkedin': 'DOMAIN_LINKEDIN',
            'facebook': 'DOMAIN_FACEBOOK',
            'twitter': 'DOMAIN_TWITTER',
            'instagram': 'DOMAIN_INSTAGRAM',
            'google': 'DOMAIN_GOOGLE',
            'microsoft': 'DOMAIN_MICROSOFT',
            'apple': 'DOMAIN_APPLE',
            'github': 'DOMAIN_GITHUB',
            'reddit': 'DOMAIN_REDDIT',
        }
        
        for key, value in domain_map.items():
            if key in domain:
                return value
        
        return f'DOMAIN_{domain.upper()}'
    
    def limit_words(self, text: str, max_words: int = 120) -> str:
        """Limit text to first N words."""
        words = text.split()
        return ' '.join(words[:max_words])
    
    def create_robust_text(self, sender: str, subject: str, body: str) -> str:
        """Create robust training text with all enhancements."""
        # Clean
        subject_clean = self.clean_text(subject)
        body_clean = self.clean_text(body)
        body_limited = self.limit_words(body_clean, 120)
        
        # Extract features
        features = self.extract_features(subject, body)
        feature_tokens = self.create_feature_tokens(features)
        
        # Extract domain
        domain_token = self.extract_domain(sender)
        
        # Weight subject 3x
        subject_weighted = f"{subject_clean} {subject_clean} {subject_clean}"
        
        # Combine: DOMAIN FEATURES SUBJECT(3x) BODY
        robust_text = f"{domain_token} {feature_tokens} SUBJECT_{subject_weighted} BODY_{body_limited}"
        
        return robust_text
