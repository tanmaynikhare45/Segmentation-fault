#!/usr/bin/env python3
"""
Simple test for gamification system
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from ai.gamification import GamificationSystem

def test_gamification():
    """Test gamification system functionality"""
    print("Testing Gamification System...")
    
    gamification = GamificationSystem()
    
    # Test user data
    test_user_data = {
        'points': 50,
        'total_complaints': 10,
        'resolved_complaints': 5,
        'fake_complaints': 1,
        'pending_complaints': 2
    }
    
    print("\nTesting get_user_stats_summary...")
    try:
        stats = gamification.get_user_stats_summary(test_user_data)
        print("SUCCESS: Stats generated successfully:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"ERROR: Stats generation failed: {e}")
    
    print("\nTesting get_badges...")
    try:
        badges = gamification.get_badges(test_user_data)
        print(f"SUCCESS: Badges generated successfully: {len(badges)} badges")
        for badge in badges:
            print(f"  {badge['name']}: {badge['description']}")
    except Exception as e:
        print(f"ERROR: Badge generation failed: {e}")
    
    print("\nTesting can_register_complaint...")
    try:
        can_register, message = gamification.can_register_complaint(50, 2)
        print(f"SUCCESS: Registration check: {can_register} - {message}")
    except Exception as e:
        print(f"ERROR: Registration check failed: {e}")
    
    print("\nGamification system test complete!")

if __name__ == "__main__":
    test_gamification()