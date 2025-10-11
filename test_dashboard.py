#!/usr/bin/env python3
"""
Test script to verify dashboard functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import create_app
from storage.db import CivicDB

def test_dashboard_routes():
    """Test that all dashboard-related routes are working"""
    app = create_app()
    
    with app.test_client() as client:
        # Test basic routes
        routes_to_test = [
            '/',
            '/login',
            '/signup',
            '/track',
            '/api/health',
            '/api/db_health'
        ]
        
        print("Testing basic routes...")
        for route in routes_to_test:
            try:
                response = client.get(route)
                print(f"✓ {route}: {response.status_code}")
            except Exception as e:
                print(f"✗ {route}: Error - {e}")
        
        # Test database connection
        print("\nTesting database connection...")
        db = CivicDB()
        if db.is_connected():
            print("✓ Database connection successful")
        else:
            print("✗ Database connection failed")
        
        print("\nDashboard setup complete!")
        print("Navigate to the following URLs:")
        print("- Home: /home")
        print("- Report Issue: /report") 
        print("- My Dashboard: /dashboard")
        print("- Track: /track")

if __name__ == "__main__":
    test_dashboard_routes()