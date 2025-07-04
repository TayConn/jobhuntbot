from typing import List
from playwright.async_api import Page
from .base_scraper import BaseScraper
from ..models.job import Job

class MonarchScraper(BaseScraper):
    """Scraper for Monarch Money jobs"""
    
    def __init__(self):
        super().__init__("monarch")
        self.base_url = "https://jobs.ashbyhq.com/monarchmoney"
    
    async def scrape_jobs(self) -> List[Job]:
        """Scrape jobs from Monarch Money careers page"""
        jobs = []
        browser, page = await self._get_browser_page()
        
        try:
            await page.goto(self.base_url, timeout=self.timeout)
            await page.wait_for_load_state("networkidle")
            
            job_links = await page.query_selector_all("a[href^='/monarchmoney/']")
            
            for link in job_links:
                try:
                    title = await link.inner_text()
                    href = await link.get_attribute("href")
                    parent = await link.evaluate_handle("el => el.closest('div')")
                    
                    location = "N/A"
                    if parent:
                        full_text = await parent.inner_text()
                        location = full_text.replace(title, "").strip()
                    
                    if title and href:
                        full_link = "https://jobs.ashbyhq.com" + href
                        categories = self._extract_categories_from_title(title)
                        job = self._create_job(title, full_link, location, categories)
                        jobs.append(job)
                        
                except Exception as e:
                    print(f"[DEBUG] Failed to parse a Monarch job: {e}")
                    
        except Exception as e:
            print(f"[ERROR] Monarch scraper failed: {e}")
        finally:
            await self._close_browser(browser)
            
        return jobs 