import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class SpeechAnalyzer:
    """Extract key features from speech text"""
    
    def __init__(self):
        self.issue_keywords = {
            'pothole': ['pothole', 'hole', 'crater', 'road damage', 'गड्ढा', 'सड़क खराब'],
            'garbage': ['garbage', 'trash', 'waste', 'litter', 'कचरा', 'गंदगी'],
            'streetlight': ['light', 'lamp', 'lighting', 'street light', 'बत्ती', 'रोशनी'],
            'traffic': ['traffic', 'jam', 'signal', 'congestion', 'ट्रैफिक'],
            'water': ['water', 'flood', 'logging', 'drainage', 'पानी', 'जल भराव'],
            'sewage': ['sewage', 'drain', 'smell', 'overflow', 'नाली', 'गंदा पानी']
        }
        
        self.location_patterns = [
            r'(?:near|at|on|in front of|behind|next to)\s+([^,.!?]+)',
            r'([^,.!?]+)\s+(?:road|street|area|market|station|hospital|school)',
            r'(?:मार्केट|स्टेशन|अस्पताल|स्कूल|रोड)\s*([^,.!?]*)',
            r'([^,.!?]+)\s*(?:के पास|में|पर)'
        ]
        
        self.urgency_keywords = {
            'high': ['urgent', 'emergency', 'dangerous', 'immediately', 'तुरंत', 'खतरनाक'],
            'medium': ['soon', 'quickly', 'problem', 'issue', 'जल्दी', 'समस्या'],
            'low': ['when possible', 'sometime', 'eventually', 'जब हो सके']
        }
    
    def analyze_speech(self, text: str) -> Dict:
        """Extract features from speech text"""
        text_lower = text.lower()
        
        return {
            'issue_type': self._detect_issue_type(text_lower),
            'location': self._extract_location(text),
            'urgency': self._detect_urgency(text_lower),
            'keywords': self._extract_keywords(text_lower),
            'complaint_summary': self._generate_summary(text)
        }
    
    def _detect_issue_type(self, text: str) -> str:
        """Detect main issue type"""
        for issue_type, keywords in self.issue_keywords.items():
            if any(keyword in text for keyword in keywords):
                return issue_type
        return 'general'
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location mentions"""
        for pattern in self.location_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                location = matches[0].strip()
                if len(location) > 2 and len(location) < 50:
                    return location
        return None
    
    def _detect_urgency(self, text: str) -> str:
        """Detect urgency level"""
        for level, keywords in self.urgency_keywords.items():
            if any(keyword in text for keyword in keywords):
                return level
        return 'medium'
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords"""
        keywords = []
        for issue_keywords in self.issue_keywords.values():
            for keyword in issue_keywords:
                if keyword in text:
                    keywords.append(keyword)
        return keywords[:5]
    
    def _generate_summary(self, text: str) -> str:
        """Generate structured complaint summary"""
        analysis = {
            'issue': self._detect_issue_type(text.lower()),
            'location': self._extract_location(text),
            'urgency': self._detect_urgency(text.lower())
        }
        
        summary = f"CIVIC COMPLAINT - {analysis['issue'].upper()}\n\n"
        summary += f"Original Report: {text}\n\n"
        
        if analysis['location']:
            summary += f"Location: {analysis['location']}\n"
        
        summary += f"Issue Type: {analysis['issue'].title()}\n"
        summary += f"Priority: {analysis['urgency'].title()}\n"
        summary += f"Status: Reported via Voice Input\n"
        
        return summary