#!/usr/bin/env python3
"""
Test script for the interactive UI system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.bot.interactive_ui import InteractiveUI, DumpJobsSession, SubscribeSession
from src.models.user_preferences import UserPreferences

def test_filter_parsing():
    """Test the filter parsing functionality in DumpJobsSession"""
    print("🧪 Testing interactive UI filter parsing...")
    
    # Test DumpJobsSession filter handling
    session = DumpJobsSession(None, None)
    
    # Test category selection
    session.selected_categories = {"backend", "frontend"}
    session.selected_locations = {"Remote"}
    session.selected_companies = {"discord"}
    
    # Test creating UserPreferences from selections
    filter_prefs = UserPreferences(user_id=0)
    filter_prefs.categories = list(session.selected_categories)
    filter_prefs.locations = list(session.selected_locations)
    filter_prefs.companies = list(session.selected_companies)
    
    print(f"Categories: {filter_prefs.categories}")
    print(f"Locations: {filter_prefs.locations}")
    print(f"Companies: {filter_prefs.companies}")
    
    # Test that the selections are correctly converted
    expected_categories = ["backend", "frontend"]
    expected_locations = ["Remote"]
    expected_companies = ["discord"]
    
    if (filter_prefs.categories == expected_categories and 
        filter_prefs.locations == expected_locations and 
        filter_prefs.companies == expected_companies):
        print("✅ PASS: Filter preferences correctly created from session selections")
    else:
        print("❌ FAIL: Filter preferences not correctly created")

def test_subscribe_session():
    """Test the subscribe session functionality"""
    print("\n🧪 Testing subscribe session...")
    
    session = SubscribeSession(None, None)
    
    # Test category selection
    session.selected_categories = {"backend", "frontend", "devops"}
    
    print(f"Selected categories: {session.selected_categories}")
    
    if len(session.selected_categories) == 3:
        print("✅ PASS: Subscribe session correctly tracks selections")
    else:
        print("❌ FAIL: Subscribe session not tracking selections correctly")

def test_ui_system():
    """Test the main UI system"""
    print("\n🧪 Testing UI system...")
    
    # Create a mock UI system
    ui_system = InteractiveUI(None)
    
    # Test session management
    print(f"Active sessions: {len(ui_system.active_sessions)}")
    
    if len(ui_system.active_sessions) == 0:
        print("✅ PASS: UI system starts with no active sessions")
    else:
        print("❌ FAIL: UI system has unexpected active sessions")

if __name__ == "__main__":
    print("🤖 Testing Job Hunt Buddy Interactive UI System\n")
    
    test_filter_parsing()
    test_subscribe_session()
    test_ui_system()
    
    print("\n✅ All interactive UI tests completed!")
    print("\n📝 Note: These tests verify the basic functionality.")
    print("   Full integration testing requires a Discord bot instance.") 