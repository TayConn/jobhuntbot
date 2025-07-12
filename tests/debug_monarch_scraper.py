#!/usr/bin/env python3
"""
Debug script for Monarch Money scraper
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_monarch_scraper():
    """Debug the Monarch Money scraper"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Run in headed mode to see what's happening
        page = await browser.new_page()
        
        print("🔍 Debugging Monarch Money Scraper...")
        print("=" * 50)
        
        # Test the correct Monarch URL
        monarch_url = "https://jobs.ashbyhq.com/monarchmoney"
        
        try:
            print(f"📄 Navigating to: {monarch_url}")
            await page.goto(monarch_url, timeout=30000)
            await page.wait_for_load_state("networkidle")
            
            # Wait a bit for any dynamic content
            print("⏳ Waiting for dynamic content to load...")
            await asyncio.sleep(3)
            
            # Check page title and basic info
            title = await page.title()
            print(f"📋 Page title: {title}")
            
            # Check if the page loaded correctly
            print("\n🔍 Checking page content...")
            
            # Look for the expected job links
            job_links = await page.query_selector_all("a[href^='/monarchmoney/']")
            print(f"   Found {len(job_links)} job links with href^='/monarchmoney/'")
            
            if job_links:
                print("   ✅ Job links found!")
                for i, link in enumerate(job_links[:5]):  # Show first 5
                    try:
                        title = await link.inner_text()
                        href = await link.get_attribute("href")
                        print(f"      {i+1}. {title} -> {href}")
                    except Exception as e:
                        print(f"      {i+1}. Error reading link: {e}")
            else:
                print("   ❌ No job links found with expected selector")
                
                # Let's look for other potential selectors
                print("\n🔍 Searching for alternative selectors...")
                
                # Look for any links
                all_links = await page.query_selector_all("a")
                print(f"   Total links on page: {len(all_links)}")
                
                # Look for links containing 'monarchmoney'
                monarch_links = await page.query_selector_all("a[href*='monarchmoney']")
                print(f"   Links containing 'monarchmoney': {len(monarch_links)}")
                
                # Look for job-related elements
                job_elements = await page.query_selector_all("[class*='job'], [class*='position'], [class*='opening']")
                print(f"   Elements with job-related classes: {len(job_elements)}")
                
                # Look for any divs that might contain jobs
                job_divs = await page.query_selector_all("div")
                print(f"   Total divs on page: {len(job_divs)}")
                
                # Check if there's any text content that looks like jobs
                page_text = await page.inner_text("body")
                if "software engineer" in page_text.lower() or "developer" in page_text.lower():
                    print("   ✅ Found job-related text on page")
                else:
                    print("   ❌ No job-related text found")
                
                # Show first few links to understand the structure
                print(f"\n📋 First 10 links on page:")
                for i, link in enumerate(all_links[:10]):
                    try:
                        title = await link.inner_text()
                        href = await link.get_attribute("href")
                        if title and href:
                            print(f"      {i+1}. {title[:50]}... -> {href}")
                    except Exception as e:
                        print(f"      {i+1}. Error reading link: {e}")
            
            # Check if there's any JavaScript that loads jobs dynamically
            print(f"\n🔍 Checking for dynamic content...")
            
            # Wait a bit more to see if anything loads
            await asyncio.sleep(5)
            
            # Check again for job links
            job_links_after_wait = await page.query_selector_all("a[href^='/monarchmoney/']")
            print(f"   Job links after waiting: {len(job_links_after_wait)}")
            
            if len(job_links_after_wait) > len(job_links):
                print("   ✅ More job links appeared after waiting!")
            elif len(job_links_after_wait) == 0:
                print("   ❌ Still no job links found")
            
            # Take a screenshot for manual inspection
            await page.screenshot(path="monarch_debug_screenshot.png")
            print(f"\n📸 Screenshot saved as monarch_debug_screenshot.png")
            
        except Exception as e:
            print(f"❌ Error during debug: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_monarch_scraper()) 