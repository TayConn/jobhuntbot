#!/usr/bin/env python3
"""
Comprehensive Reddit job board debug script
Checks for new jobs, different sections, and potential indexing issues
"""

import asyncio
import json
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import time

async def debug_reddit_comprehensive():
    """Comprehensive debug of Reddit job board"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Run in headed mode to see what's happening
        page = await browser.new_page()
        
        print("🔍 Starting comprehensive Reddit job board debug...")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Navigate to Reddit job board
            print("\n📄 Navigating to Reddit job board...")
            await page.goto("https://boards.greenhouse.io/reddit", timeout=30000)
            await page.wait_for_load_state("networkidle")
            
            # Wait a bit for any dynamic content
            print("⏳ Waiting for dynamic content to load...")
            await asyncio.sleep(3)
            
            # Check page title and basic info
            title = await page.title()
            print(f"📋 Page title: {title}")
            
            # Look for any "New" or "Featured" sections
            print("\n🔍 Checking for special job sections...")
            
            # Check for "New" indicators
            new_indicators = await page.query_selector_all("[class*='new'], [class*='recent'], [class*='featured']")
            if new_indicators:
                print(f"✅ Found {len(new_indicators)} potential 'new' indicators")
                for i, indicator in enumerate(new_indicators[:5]):  # Show first 5
                    text = await indicator.inner_text()
                    print(f"   {i+1}. {text[:100]}...")
            else:
                print("❌ No 'new' indicators found")
            
            # Check for any job count information
            job_count_elements = await page.query_selector_all("[class*='count'], [class*='total'], [class*='jobs']")
            for elem in job_count_elements:
                text = await elem.inner_text()
                if any(word in text.lower() for word in ['job', 'position', 'opening']):
                    print(f"📊 Job count info: {text}")
            
            # Now scrape jobs with detailed logging
            print("\n🔍 Scraping jobs with detailed logging...")
            all_jobs = []
            page_num = 1
            
            while True:
                print(f"\n📄 Page {page_num}:")
                
                # Wait for jobs to load
                await page.wait_for_selector("tr.job-post", timeout=10000)
                
                # Get all job rows
                job_rows = await page.query_selector_all("tr.job-post")
                print(f"   Found {len(job_rows)} job rows")
                
                page_jobs = []
                for i, row in enumerate(job_rows):
                    try:
                        # Get job details
                        a_tag = await row.query_selector("a[href*='/reddit/jobs/']")
                        title_p = await row.query_selector("p.body--medium")
                        location_p = await row.query_selector("p.body--metadata")
                        
                        title = await title_p.inner_text() if title_p else "N/A"
                        href = await a_tag.get_attribute("href") if a_tag else ""
                        location = await location_p.inner_text() if location_p else "N/A"
                        
                        if title != "N/A" and href:
                            full_link = href if href.startswith("http") else f"https://boards.greenhouse.io{href}"
                            
                            # Extract job ID from URL
                            job_id = href.split('/')[-1] if href else "unknown"
                            
                            # Check if this is the missing job
                            if job_id == "6993468":
                                print(f"🎯 FOUND THE MISSING JOB!")
                                print(f"   Title: {title}")
                                print(f"   Location: {location}")
                                print(f"   URL: {full_link}")
                                print(f"   Row index: {i}")
                            
                            page_jobs.append({
                                'id': job_id,
                                'title': title,
                                'location': location,
                                'url': full_link
                            })
                            
                            # Print first few jobs on each page
                            if i < 3:
                                print(f"   {i+1}. [{job_id}] {title} - {location}")
                    
                    except Exception as e:
                        print(f"   ❌ Error parsing job {i}: {e}")
                
                all_jobs.extend(page_jobs)
                print(f"   Total jobs so far: {len(all_jobs)}")
                
                # Check pagination
                next_button = await page.query_selector("button.pagination__next")
                if not next_button:
                    next_button = await page.query_selector("a.next_page")
                
                if not next_button:
                    print("   ✅ No more pages")
                    break
                
                # Check if button is disabled
                is_disabled = await next_button.get_attribute("aria-disabled")
                if is_disabled == "true":
                    print("   ✅ Next button is disabled")
                    break
                
                # Click next page
                print("   ➡️ Clicking next page...")
                await next_button.click()
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(2)  # Wait for content to load
                
                page_num += 1
                
                # Limit to first 10 pages for debugging
                if page_num > 10:
                    print("   ⚠️ Stopping at 10 pages for debugging")
                    break
            
            # Summary
            print(f"\n📊 SUMMARY:")
            print(f"   Total jobs found: {len(all_jobs)}")
            print(f"   Pages scraped: {page_num}")
            
            # Check for job ID 6993468
            missing_job_found = any(job['id'] == '6993468' for job in all_jobs)
            if missing_job_found:
                print("   ✅ Job ID 6993468 was found!")
            else:
                print("   ❌ Job ID 6993468 was NOT found")
            
            # Save results
            with open('reddit_debug_results.json', 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'total_jobs': len(all_jobs),
                    'pages_scraped': page_num,
                    'missing_job_found': missing_job_found,
                    'jobs': all_jobs
                }, f, indent=2)
            
            print(f"\n💾 Results saved to reddit_debug_results.json")
            
            # Check for compliance jobs specifically
            compliance_jobs = [job for job in all_jobs if 'compliance' in job['title'].lower()]
            print(f"\n🔍 Compliance jobs found: {len(compliance_jobs)}")
            for job in compliance_jobs:
                print(f"   - [{job['id']}] {job['title']} - {job['location']}")
            
        except Exception as e:
            print(f"❌ Error during debug: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_reddit_comprehensive()) 