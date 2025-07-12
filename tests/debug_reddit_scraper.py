#!/usr/bin/env python3
"""
Debug script for Reddit scraper to investigate missing jobs
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scrapers.reddit_scraper import RedditScraper
from playwright.async_api import async_playwright

async def debug_reddit_scraper():
    print("🔍 Debugging Reddit Scraper - Investigating Missing Jobs\n" + "="*70)
    
    # Test the scraper normally first
    scraper = RedditScraper()
    jobs = await scraper.scrape_jobs(filter_us_only=True)
    
    print(f"Total jobs found: {len(jobs)}")
    
    # Check if the specific job is in our results
    target_job_id = "6993468"
    target_job_found = False
    
    for job in jobs:
        if target_job_id in job.link:
            print(f"✅ Found target job: {job.title}")
            target_job_found = True
            break
    
    if not target_job_found:
        print(f"❌ Target job {target_job_id} NOT found in scraper results")
        
        # Let's manually check the Reddit job board
        print("\n🔍 Manually checking Reddit job board...")
        await manual_check_reddit_jobs()
    
    print(f"\n✅ Debug complete.")

async def manual_check_reddit_jobs():
    """Manually check the Reddit job board to see what's there"""
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch()
    page = await browser.new_page()
    
    try:
        await page.goto("https://boards.greenhouse.io/reddit", timeout=60000)
        await page.wait_for_load_state("networkidle")
        
        print("Checking first page...")
        
        # Get all job rows
        job_rows = await page.query_selector_all("tr.job-post")
        print(f"Found {len(job_rows)} job rows on first page")
        
        # Check for the specific job
        target_found = False
        for i, row in enumerate(job_rows[:10]):  # Check first 10 jobs
            try:
                a_tag = await row.query_selector("a[href*='/reddit/jobs/']")
                if a_tag:
                    href = await a_tag.get_attribute("href")
                    if href and "6993468" in href:
                        print(f"✅ Found target job on page 1, row {i+1}")
                        target_found = True
                        break
            except Exception as e:
                print(f"Error checking row {i}: {e}")
        
        if not target_found:
            print("Target job not found on first page, checking pagination...")
            
            # Check if there's a next button
            next_button = await page.query_selector("button.pagination__next")
            if next_button:
                is_disabled = await next_button.get_attribute("aria-disabled")
                print(f"Next button found, disabled: {is_disabled}")
                
                if is_disabled != "true":
                    print("Clicking next button...")
                    await next_button.click()
                    await page.wait_for_load_state("networkidle")
                    
                    # Check second page
                    job_rows = await page.query_selector_all("tr.job-post")
                    print(f"Found {len(job_rows)} job rows on second page")
                    
                    for i, row in enumerate(job_rows[:10]):
                        try:
                            a_tag = await row.query_selector("a[href*='/reddit/jobs/']")
                            if a_tag:
                                href = await a_tag.get_attribute("href")
                                if href and "6993468" in href:
                                    print(f"✅ Found target job on page 2, row {i+1}")
                                    target_found = True
                                    break
                        except Exception as e:
                            print(f"Error checking row {i}: {e}")
                else:
                    print("Next button is disabled - no more pages")
            else:
                print("No next button found")
        
        if not target_found:
            print("❌ Target job not found on any page")
            
            # Let's check more pages to be thorough
            print("\nChecking additional pages...")
            page_num = 3
            while page_num <= 5:  # Check up to 5 pages
                next_button = await page.query_selector("button.pagination__next")
                if next_button:
                    is_disabled = await next_button.get_attribute("aria-disabled")
                    if is_disabled == "true":
                        print(f"Page {page_num-1} was the last page")
                        break
                    
                    await next_button.click()
                    await page.wait_for_load_state("networkidle")
                    
                    job_rows = await page.query_selector_all("tr.job-post")
                    print(f"Found {len(job_rows)} job rows on page {page_num}")
                    
                    # Check for target job
                    for i, row in enumerate(job_rows[:10]):
                        try:
                            a_tag = await row.query_selector("a[href*='/reddit/jobs/']")
                            if a_tag:
                                href = await a_tag.get_attribute("href")
                                if href and "6993468" in href:
                                    print(f"✅ Found target job on page {page_num}, row {i+1}")
                                    target_found = True
                                    break
                        except Exception as e:
                            print(f"Error checking row {i}: {e}")
                    
                    if target_found:
                        break
                    
                    page_num += 1
                else:
                    break
            
            # Let's also check if there are any jobs with "compliance" in the title
            print("\nChecking for any compliance-related jobs...")
            compliance_count = 0
            for row in job_rows:
                try:
                    title_p = await row.query_selector("p.body--medium")
                    if title_p:
                        title = await title_p.inner_text()
                        if "compliance" in title.lower():
                            compliance_count += 1
                            print(f"Found compliance job: {title}")
                except:
                    pass
            
            print(f"Total compliance jobs found manually: {compliance_count}")
            
            # Check for any filtering options
            print("\nChecking for filtering options...")
            filters = await page.query_selector_all("select, input[type='checkbox'], button[data-filter]")
            if filters:
                print(f"Found {len(filters)} potential filter elements")
                for i, filter_elem in enumerate(filters[:5]):
                    try:
                        tag_name = await filter_elem.evaluate("el => el.tagName")
                        print(f"Filter {i+1}: {tag_name}")
                    except:
                        pass
            else:
                print("No obvious filter elements found")
    
    except Exception as e:
        print(f"Error during manual check: {e}")
    
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    asyncio.run(debug_reddit_scraper()) 