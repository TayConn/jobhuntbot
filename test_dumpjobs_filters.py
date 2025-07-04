#!/usr/bin/env python3
"""
Test script for the new dumpjobs filtering functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.bot.commands import JobBotCommands
from src.models.user_preferences import UserPreferences

def test_filter_parsing():
    """Test the filter parsing functionality"""
    print("🧪 Testing dumpjobs filter parsing...")
    
    # Create a mock commands instance
    commands = JobBotCommands(None, None, None)
    
    # Test cases
    test_cases = [
        # Simple single filter
        ('category="backend"', {'categories': ['backend'], 'locations': [], 'companies': []}),
        
        # Multiple categories
        ('category="backend, frontend, devops"', {'categories': ['backend', 'frontend', 'devops'], 'locations': [], 'companies': []}),
        
        # Multiple filters
        ('category="backend" location="Remote"', {'categories': ['backend'], 'locations': ['Remote'], 'companies': []}),
        
        # All three filter types
        ('category="backend, frontend" location="Remote, San Francisco" company="discord, reddit"', 
         {'categories': ['backend', 'frontend'], 'locations': ['Remote', 'San Francisco'], 'companies': ['discord', 'reddit']}),
        
        # Case insensitive
        ('CATEGORY="backend" LOCATION="Remote"', {'categories': ['backend'], 'locations': ['Remote'], 'companies': []}),
        
        # Empty filter
        ('', None),
        
        # Invalid format
        ('invalid format', None),
    ]
    
    for i, (filter_str, expected) in enumerate(test_cases, 1):
        print(f"\nTest {i}: {filter_str}")
        
        result = commands._parse_dump_filters(filter_str)
        
        if expected is None:
            if result is None:
                print("✅ PASS: Expected None, got None")
            else:
                print(f"❌ FAIL: Expected None, got {result}")
        else:
            if result is None:
                print("❌ FAIL: Expected filter prefs, got None")
            else:
                # Check if the result matches expected
                actual = {
                    'categories': result.categories,
                    'locations': result.locations,
                    'companies': result.companies
                }
                
                if actual == expected:
                    print("✅ PASS: Filter parsing correct")
                else:
                    print(f"❌ FAIL: Expected {expected}, got {actual}")

def test_job_filtering():
    """Test job filtering with UserPreferences"""
    print("\n🧪 Testing job filtering...")
    
    from src.models.job import Job
    
    # Create test jobs
    test_jobs = [
        Job("Backend Engineer", "https://example.com/1", "San Francisco", "discord", ["backend", "software engineer"]),
        Job("Frontend Developer", "https://example.com/2", "Remote", "reddit", ["frontend", "developer"]),
        Job("DevOps Engineer", "https://example.com/3", "New York", "monarch", ["devops", "engineer"]),
        Job("Product Manager", "https://example.com/4", "Remote", "discord", ["product manager"]),
    ]
    
    # Test 1: Filter by category only
    print("\nTest 1: Filter by category only")
    filter_prefs = UserPreferences(user_id=0)
    filter_prefs.categories = ["backend", "frontend"]
    
    filtered_jobs = [job for job in test_jobs if job.matches_user_preferences(filter_prefs)]
    print(f"Categories filter: {filter_prefs.categories}")
    print(f"Expected: 2 jobs (Backend Engineer, Frontend Developer)")
    print(f"Got: {len(filtered_jobs)} jobs")
    for job in filtered_jobs:
        print(f"  - {job.title}")
    
    if len(filtered_jobs) == 2:
        print("✅ PASS: Category filtering works")
    else:
        print("❌ FAIL: Category filtering failed")
    
    # Test 2: Filter by location only
    print("\nTest 2: Filter by location only")
    filter_prefs = UserPreferences(user_id=0)
    filter_prefs.locations = ["Remote"]
    
    filtered_jobs = [job for job in test_jobs if job.matches_user_preferences(filter_prefs)]
    print(f"Location filter: {filter_prefs.locations}")
    print(f"Expected: 2 jobs (Frontend Developer, Product Manager)")
    print(f"Got: {len(filtered_jobs)} jobs")
    for job in filtered_jobs:
        print(f"  - {job.title}")
    
    if len(filtered_jobs) == 2:
        print("✅ PASS: Location filtering works")
    else:
        print("❌ FAIL: Location filtering failed")
    
    # Test 3: Filter by company only
    print("\nTest 3: Filter by company only")
    filter_prefs = UserPreferences(user_id=0)
    filter_prefs.companies = ["discord"]
    
    filtered_jobs = [job for job in test_jobs if job.matches_user_preferences(filter_prefs)]
    print(f"Company filter: {filter_prefs.companies}")
    print(f"Expected: 2 jobs (Backend Engineer, Product Manager)")
    print(f"Got: {len(filtered_jobs)} jobs")
    for job in filtered_jobs:
        print(f"  - {job.title}")
    
    if len(filtered_jobs) == 2:
        print("✅ PASS: Company filtering works")
    else:
        print("❌ FAIL: Company filtering failed")
    
    # Test 4: Combined filters (AND logic between different types)
    print("\nTest 4: Combined filters")
    filter_prefs = UserPreferences(user_id=0)
    filter_prefs.categories = ["backend", "frontend"]
    filter_prefs.locations = ["Remote"]
    filter_prefs.companies = ["discord"]
    
    filtered_jobs = [job for job in test_jobs if job.matches_user_preferences(filter_prefs)]
    print(f"Combined filter: categories={filter_prefs.categories}, locations={filter_prefs.locations}, companies={filter_prefs.companies}")
    print(f"Expected: 0 jobs (no job matches all three criteria)")
    print(f"Got: {len(filtered_jobs)} jobs")
    for job in filtered_jobs:
        print(f"  - {job.title}")
    
    if len(filtered_jobs) == 0:
        print("✅ PASS: Combined filtering works (AND logic between filter types)")
    else:
        print("❌ FAIL: Combined filtering failed")
    
    # Test 5: Combined filters that should match
    print("\nTest 5: Combined filters that should match")
    filter_prefs = UserPreferences(user_id=0)
    filter_prefs.categories = ["backend", "frontend", "product manager"]
    filter_prefs.locations = ["Remote"]
    filter_prefs.companies = ["discord"]
    
    filtered_jobs = [job for job in test_jobs if job.matches_user_preferences(filter_prefs)]
    print(f"Combined filter: categories={filter_prefs.categories}, locations={filter_prefs.locations}, companies={filter_prefs.companies}")
    print(f"Expected: 1 job (Product Manager at discord in Remote)")
    print(f"Got: {len(filtered_jobs)} jobs")
    for job in filtered_jobs:
        print(f"  - {job.title}")
    
    if len(filtered_jobs) == 1 and filtered_jobs[0].title == "Product Manager":
        print("✅ PASS: Combined filtering works correctly")
    else:
        print("❌ FAIL: Combined filtering failed")

if __name__ == "__main__":
    print("🤖 Testing Job Hunt Buddy dumpjobs filtering functionality\n")
    
    test_filter_parsing()
    test_job_filtering()
    
    print("\n✅ All tests completed!") 