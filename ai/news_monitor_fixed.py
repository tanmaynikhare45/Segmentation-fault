import logging
import requests
import asyncio
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re
import json

logger = logging.getLogger(__name__)

class NewsMonitor:
    """Enhanced news and social media monitor with fallback data"""
    
    CIVIC_KEYWORDS = [
        "pothole", "road damage", "garbage", "waste", "streetlight", "street light",
        "waterlogging", "water logging", "encroachment", "illegal construction",
        "traffic jam", "pollution", "sewage", "broken road", "civic issue",
        "सड़क", "गड्ढा", "कचरा", "गंदगी", "बत्ती", "जल भराव", "ट्रैफिक", "प्रदूषण"
    ]
    
    def __init__(self, news_api_key: str = None, twitter_bearer: str = None):
        import os
        self.news_api_key = news_api_key or os.getenv("NEWS_API_KEY", "your_news_api_key")
        self.twitter_bearer = twitter_bearer or os.getenv("TWITTER_BEARER_TOKEN", "your_twitter_bearer_token")
        self.news_base_url = "https://newsapi.org/v2/everything"
        self.twitter_base_url = "https://api.twitter.com/2/tweets/search/recent"
        logger.info("Enhanced NewsMonitor initialized")
    
    def _get_fallback_data(self, city: str) -> Dict[str, List[Dict]]:
        """Generate fallback civic issues data"""
        news_data = [
            {
                'title': f'{city} Road Maintenance Issues Reported',
                'description': 'Multiple potholes and road damage reported by citizens in various areas',
                'url': 'https://example.com/news1',
                'publishedAt': datetime.now().isoformat()
            },
            {
                'title': f'{city} Garbage Collection Delays',
                'description': 'Waste management issues causing concern among residents',
                'url': 'https://example.com/news2', 
                'publishedAt': (datetime.now() - timedelta(hours=2)).isoformat()
            },
            {
                'title': f'{city} Street Light Maintenance Required',
                'description': 'Several areas reporting non-functional street lighting',
                'url': 'https://example.com/news3',
                'publishedAt': (datetime.now() - timedelta(hours=4)).isoformat()
            }
        ]
        
        twitter_data = [
            {
                'id': '1234567890',
                'text': f'Pothole on main road in {city} needs immediate attention #civicissue',
                'created_at': datetime.now().isoformat(),
                'public_metrics': {'retweet_count': 5, 'like_count': 12}
            },
            {
                'id': '1234567891', 
                'text': f'Garbage not collected for 3 days in {city} area #waste #municipal',
                'created_at': (datetime.now() - timedelta(hours=1)).isoformat(),
                'public_metrics': {'retweet_count': 8, 'like_count': 15}
            }
        ]
        
        return {"news": news_data, "twitter": twitter_data, "reddit": []}
    
    def generate_complaints_from_news(self) -> List[Dict]:
        """Generate complaints with fallback data"""
        try:
            # Use fallback data for demo
            city = "Gwalior"
            all_sources = self._get_fallback_data(city)
            issues = self.extract_civic_issues(all_sources)
            
            complaints = []
            for issue in issues:
                complaint = {
                    'issue_type': issue['issue_type'],
                    'description': f"[{issue['source'].upper()}] {issue['title']} - {issue['description'][:200]}",
                    'source_url': issue['url'],
                    'auto_generated': True,
                    'source_type': issue['source'],
                    'published_date': issue['published_at'],
                    'relevance_score': issue['score'],
                    'keywords': issue['keywords']
                }
                complaints.append(complaint)
            
            logger.info(f"Generated {len(complaints)} complaints from sources")
            return complaints
            
        except Exception as e:
            logger.error(f"Failed to generate complaints: {e}")
            return []
    
    def extract_civic_issues(self, all_sources: Dict[str, List[Dict]]) -> List[Dict]:
        """Extract civic issues from all sources"""
        issues = []
        
        # Process news articles
        for article in all_sources.get('news', []):
            issue = self._process_news_article(article)
            if issue:
                issues.append(issue)
        
        # Process Twitter posts
        for tweet in all_sources.get('twitter', []):
            issue = self._process_twitter_post(tweet)
            if issue:
                issues.append(issue)
        
        # Sort by relevance/recency
        issues.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return issues[:20]
    
    def _process_news_article(self, article: Dict) -> Optional[Dict]:
        """Process news article for civic issues"""
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        content = f"{title} {description}"
        
        found_keywords = [kw for kw in self.CIVIC_KEYWORDS if kw.lower() in content]
        
        if found_keywords:
            issue_type = self._classify_issue(content)
            score = len(found_keywords) * 2 + (1 if 'breaking' in content else 0)
            
            return {
                'title': article.get('title'),
                'description': article.get('description'),
                'url': article.get('url'),
                'published_at': article.get('publishedAt'),
                'issue_type': issue_type,
                'keywords': found_keywords,
                'source': 'news',
                'score': score
            }
        return None
    
    def _process_twitter_post(self, tweet: Dict) -> Optional[Dict]:
        """Process Twitter post for civic issues"""
        text = tweet.get('text', '').lower()
        found_keywords = [kw for kw in self.CIVIC_KEYWORDS if kw.lower() in text]
        
        if found_keywords:
            issue_type = self._classify_issue(text)
            metrics = tweet.get('public_metrics', {})
            engagement = metrics.get('retweet_count', 0) + metrics.get('like_count', 0)
            score = len(found_keywords) + min(engagement / 10, 5)
            
            return {
                'title': f"Twitter: {text[:100]}...",
                'description': text,
                'url': f"https://twitter.com/i/web/status/{tweet.get('id')}",
                'published_at': tweet.get('created_at'),
                'issue_type': issue_type,
                'keywords': found_keywords,
                'source': 'twitter',
                'score': score,
                'engagement': engagement
            }
        return None
    
    def _classify_issue(self, content: str) -> str:
        """Enhanced issue classification"""
        content = content.lower()
        
        classifications = {
            'pothole': ['pothole', 'road damage', 'गड्ढा', 'सड़क', 'broken road'],
            'garbage': ['garbage', 'waste', 'कचरा', 'गंदगी', 'trash', 'litter'],
            'streetlight': ['light', 'lighting', 'बत्ती', 'street light', 'lamp'],
            'waterlogging': ['water', 'flood', 'जल भराव', 'waterlog', 'drainage'],
            'traffic': ['traffic', 'jam', 'congestion', 'ट्रैफिक'],
            'pollution': ['pollution', 'smoke', 'प्रदूषण', 'air quality'],
            'encroachment': ['encroachment', 'illegal', 'unauthorized']
        }
        
        for issue_type, keywords in classifications.items():
            if any(keyword in content for keyword in keywords):
                return issue_type
        
        return 'unknown'