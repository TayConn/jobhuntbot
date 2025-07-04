#!/usr/bin/env python3
"""
Simple test script to verify the code is working as expected before running
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported successfully"""
    try:
        print("Testing imports...")
        
        # Test config
        from src.utils.config import Config
        print("✅ Config imported successfully")
        
        # Test models
        from src.models.job import Job
        from src.models.user_preferences import UserPreferences
        print("✅ Models imported successfully")
        
        # Test scrapers
        from src.scrapers.discord_scraper import DiscordScraper
        from src.scrapers.reddit_scraper import RedditScraper
        from src.scrapers.monarch_scraper import MonarchScraper
        print("✅ Scrapers imported successfully")
        
        # Test services
        from src.services.storage_service import StorageService
        from src.services.notification_service import NotificationService
        from src.services.job_monitor import JobMonitor
        print("✅ Services imported successfully")
        
        # Test bot
        from src.bot.discord_bot import JobHuntBot
        print("✅ Bot imported successfully")
        
        print("\n🎉 All imports successful! The refactored structure is working.")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_job_model():
    """Test the Job model functionality"""
    try:
        from src.models.job import Job
        
        # Create a test job
        job = Job(
            title="Software Engineer",
            link="https://example.com/job",
            location="San Francisco, CA",
            company="test_company",
            categories=["software engineer", "backend"]
        )
        
        print(f"✅ Job model test passed: {job.title} at {job.company}")
        return True
        
    except Exception as e:
        print(f"❌ Job model test failed: {e}")
        return False

def test_user_preferences():
    """Test the UserPreferences model functionality"""
    try:
        from src.models.user_preferences import UserPreferences
        
        # Create test preferences
        prefs = UserPreferences(user_id=12345)
        prefs.add_category("software engineer")
        prefs.add_location("San Francisco")
        prefs.add_company("discord")
        
        print(f"✅ UserPreferences test passed: {len(prefs.categories)} categories")
        return True
        
    except Exception as e:
        print(f"❌ UserPreferences test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing refactored Job Hunt Bot...\n")
    
    tests = [
        test_imports,
        test_job_model,
        test_user_preferences
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The refactor is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.") 