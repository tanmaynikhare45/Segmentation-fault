#!/usr/bin/env python3
"""
Background tasks for updating news and social media data
"""

import threading
import time
import logging
from datetime import datetime
from ai.news_monitor import NewsMonitor

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    """Manages background tasks for the application"""
    
    def __init__(self):
        self.news_monitor = NewsMonitor()
        self.running = False
        self.news_cache = []
        self.last_update = None
        
    def start_background_tasks(self):
        """Start background tasks"""
        if not self.running:
            self.running = True
            # Start news update thread
            news_thread = threading.Thread(target=self._news_update_loop, daemon=True)
            news_thread.start()
            logger.info("Background tasks started")
    
    def stop_background_tasks(self):
        """Stop background tasks"""
        self.running = False
        logger.info("Background tasks stopped")
    
    def _news_update_loop(self):
        """Background loop to update news data every 30 minutes"""
        while self.running:
            try:
                logger.info("Updating news and social media data...")
                self.news_cache = self.news_monitor.generate_complaints_from_news()
                self.last_update = datetime.now()
                logger.info(f"Updated {len(self.news_cache)} news items")
            except Exception as e:
                logger.error(f"Error updating news data: {e}")
            
            # Wait 30 minutes before next update
            time.sleep(1800)  # 30 minutes
    
    def get_fresh_news(self):
        """Get fresh news data"""
        if not self.news_cache or not self.last_update:
            # First time or no cache, get data immediately
            try:
                self.news_cache = self.news_monitor.generate_complaints_from_news()
                self.last_update = datetime.now()
            except Exception as e:
                logger.error(f"Error getting fresh news: {e}")
                return []
        
        return self.news_cache

# Global instance
task_manager = BackgroundTaskManager()