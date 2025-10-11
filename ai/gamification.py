"""
Gamification system for complaint registration.

Points System:
- Complaint submitted: 0 points (neutral)
- Complaint resolved: +10 points
- Complaint marked as fake: -15 points
- Multiple unresolved complaints: -5 points per complaint after threshold
- User blocked when points fall below threshold
"""

import logging
from typing import Dict, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class GamificationSystem:
    """
    Manages user points and gamification rules for complaint registration.
    """
    
    # Point values
    POINTS_RESOLVED = 10
    POINTS_FAKE_PENALTY = -5
    POINTS_UNRESOLVED_PENALTY = -5
    
    # Thresholds
    MIN_POINTS_TO_REGISTER = -20  # Users below this cannot register complaints
    PERMANENT_BAN_THRESHOLD = -40  # Users below this are permanently banned
    MAX_PENDING_COMPLAINTS = 2  # Maximum pending complaints before blocking
    
    # Badges and levels
    LEVELS = [
        {"name": "Novice Citizen", "min_points": 0, "color": "#gray"},
        {"name": "Active Citizen", "min_points": 50, "color": "#blue"},
        {"name": "Super Citizen", "min_points": 100, "color": "#green"},
        {"name": "Elite Citizen", "min_points": 200, "color": "#purple"},
        {"name": "Guardian Citizen", "min_points": 500, "color": "#gold"},
    ]
    
    def __init__(self):
        logger.info("Gamification system initialized")
    
    def is_permanently_banned(self, user_points: int) -> bool:
        """
        Check if user is permanently banned.
        
        Args:
            user_points: Current user points
            
        Returns:
            True if user is permanently banned
        """
        return user_points < self.PERMANENT_BAN_THRESHOLD
    
    def can_register_complaint(self, user_points: int, pending_count: int) -> Tuple[bool, str]:
        """
        Check if user can register a new complaint.
        
        Args:
            user_points: Current user points
            pending_count: Number of pending complaints
            
        Returns:
            Tuple of (can_register, reason_message)
        """
        # Check if user is permanently banned
        if user_points < self.PERMANENT_BAN_THRESHOLD:
            return False, (
                f"Your account has been permanently banned due to excessive fake complaints ({user_points} points). "
                f"This account cannot be used anymore. Please contact support if you believe this is an error."
            )
        
        # Check if user has too many negative points
        if user_points < self.MIN_POINTS_TO_REGISTER:
            return False, (
                f"Your account is temporarily blocked due to low points ({user_points}). "
                f"Please wait for your pending complaints to be resolved to restore your account. "
                f"You need at least {self.MIN_POINTS_TO_REGISTER} points to register complaints."
            )
        
        # Check if user has too many pending complaints
        if pending_count >= self.MAX_PENDING_COMPLAINTS:
            return False, (
                f"You have {pending_count} pending complaints. "
                f"Please wait for some of them to be resolved before registering new ones. "
                f"Maximum allowed pending complaints: {self.MAX_PENDING_COMPLAINTS}."
            )
        
        return True, "You can register a complaint."
    
    def calculate_points_for_resolved(self, is_fake: bool) -> int:
        """
        Calculate points to award when a complaint is resolved.
        
        Args:
            is_fake: Whether the complaint was marked as fake
            
        Returns:
            Points to award (positive for genuine, negative for fake)
        """
        if is_fake:
            return 0  # No points for fake complaints being resolved
        return self.POINTS_RESOLVED
    
    def calculate_points_for_fake_detection(self) -> int:
        """
        Calculate penalty points when a complaint is marked as fake.
        
        Returns:
            Negative points (penalty)
        """
        return self.POINTS_FAKE_PENALTY
    
    def calculate_unresolved_penalty(self, pending_count: int) -> int:
        """
        Calculate penalty for having too many unresolved complaints.
        
        Args:
            pending_count: Number of pending complaints
            
        Returns:
            Penalty points (0 if below threshold, negative otherwise)
        """
        if pending_count <= self.MAX_PENDING_COMPLAINTS:
            return 0
        
        excess = pending_count - self.MAX_PENDING_COMPLAINTS
        return excess * self.POINTS_UNRESOLVED_PENALTY
    
    def get_user_level(self, points: int) -> Dict:
        """
        Get user's current level based on points.
        
        Args:
            points: User's current points
            
        Returns:
            Dictionary with level information
        """
        current_level = self.LEVELS[0]
        next_level = None
        
        for i, level in enumerate(self.LEVELS):
            if points >= level["min_points"]:
                current_level = level
                if i + 1 < len(self.LEVELS):
                    next_level = self.LEVELS[i + 1]
            else:
                break
        
        return {
            "current_level": current_level,
            "next_level": next_level,
            "progress_to_next": self._calculate_progress(points, current_level, next_level)
        }
    
    def _calculate_progress(self, points: int, current_level: Dict, next_level: Optional[Dict]) -> float:
        """
        Calculate progress percentage to next level.
        
        Args:
            points: User's current points
            current_level: Current level info
            next_level: Next level info (or None if at max level)
            
        Returns:
            Progress percentage (0-100)
        """
        if next_level is None:
            return 100.0
        
        current_min = current_level["min_points"]
        next_min = next_level["min_points"]
        
        if next_min <= current_min:
            return 100.0
        
        progress = ((points - current_min) / (next_min - current_min)) * 100
        return max(0.0, min(100.0, progress))
    
    def get_user_stats_summary(self, user_data: Dict) -> Dict:
        """
        Generate a comprehensive stats summary for the user.
        
        Args:
            user_data: User document from database
            
        Returns:
            Dictionary with formatted stats
        """
        points = user_data.get("points", 0)
        total_complaints = user_data.get("total_complaints", 0)
        resolved_complaints = user_data.get("resolved_complaints", 0)
        fake_complaints = user_data.get("fake_complaints", 0)
        pending_complaints = user_data.get("pending_complaints", 0)
        
        # Calculate success rate
        success_rate = 0.0
        if total_complaints > 0:
            success_rate = (resolved_complaints / total_complaints) * 100
        
        # Get level info
        level_info = self.get_user_level(points)
        
        # Check if user can register
        can_register, message = self.can_register_complaint(points, pending_complaints)
        
        return {
            "points": points,
            "level": level_info["current_level"]["name"],
            "level_color": level_info["current_level"]["color"],
            "next_level": level_info["next_level"]["name"] if level_info["next_level"] else "Max Level",
            "progress_to_next": level_info["progress_to_next"],
            "total_complaints": total_complaints,
            "resolved_complaints": resolved_complaints,
            "fake_complaints": fake_complaints,
            "pending_complaints": pending_complaints,
            "success_rate": round(success_rate, 1),
            "can_register": can_register,
            "registration_message": message,
            "is_blocked": not can_register
        }
    
    def get_badges(self, user_data: Dict) -> list:
        """
        Get list of badges earned by the user.
        
        Args:
            user_data: User document from database
            
        Returns:
            List of badge dictionaries
        """
        badges = []
        
        resolved = user_data.get("resolved_complaints", 0)
        total = user_data.get("total_complaints", 0)
        points = user_data.get("points", 0)
        
        # First complaint badge
        if total >= 1:
            badges.append({
                "name": "First Step",
                "description": "Registered your first complaint",
                "icon": "🎯"
            })
        
        # Resolved complaints badges
        if resolved >= 1:
            badges.append({
                "name": "Problem Solver",
                "description": "Had your first complaint resolved",
                "icon": "✅"
            })
        
        if resolved >= 5:
            badges.append({
                "name": "Active Reporter",
                "description": "5 complaints resolved",
                "icon": "🌟"
            })
        
        if resolved >= 10:
            badges.append({
                "name": "Community Hero",
                "description": "10 complaints resolved",
                "icon": "🏆"
            })
        
        if resolved >= 25:
            badges.append({
                "name": "Civic Champion",
                "description": "25 complaints resolved",
                "icon": "👑"
            })
        
        # High points badges
        if points >= 100:
            badges.append({
                "name": "Point Master",
                "description": "Earned 100+ points",
                "icon": "💎"
            })
        
        if points >= 500:
            badges.append({
                "name": "Legendary Citizen",
                "description": "Earned 500+ points",
                "icon": "🔥"
            })
        
        # Perfect record badge
        if total >= 5 and user_data.get("fake_complaints", 0) == 0:
            badges.append({
                "name": "Trustworthy",
                "description": "No fake complaints detected",
                "icon": "🛡️"
            })
        
        return badges
