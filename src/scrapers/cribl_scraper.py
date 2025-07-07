from typing import List
from playwright.async_api import Page
from .base_scraper import BaseScraper
from ..models.job import Job

class CriblScraper(BaseScraper):
    """Scraper for Cribl jobs"""
    
    def __init__(self):
        super().__init__("cribl")
        self.base_url = "https://job-boards.greenhouse.io/cribl"
    
    async def scrape_jobs(self, filter_us_only: bool = True) -> List[Job]:
        """Scrape jobs from Cribl careers page"""
        jobs = []
        browser, page = await self._get_browser_page()
        
        try:
            await page.goto(self.base_url, timeout=self.timeout)
            await page.wait_for_load_state("networkidle")
            
            while True:
                job_rows = await page.query_selector_all("tr.job-post")
                
                for row in job_rows:
                    try:
                        a_tag = await row.query_selector("a[href*='/cribl/jobs/']")
                        title_p = await row.query_selector("p.body--medium")
                        location_p = await row.query_selector("p.body--metadata")
                        
                        title = await title_p.inner_text() if title_p else "N/A"
                        href = await a_tag.get_attribute("href") if a_tag else ""
                        location = await location_p.inner_text() if location_p else "N/A"
                        full_link = href if href.startswith("http") else f"https://boards.greenhouse.io{href}"
                        
                        if title != "N/A" and full_link:
                            categories = self._extract_categories_from_title(title)
                            job = self._create_job(title, full_link, location, categories)
                            jobs.append(job)
                            
                    except Exception as e:
                        print(f"[DEBUG] Error parsing Cribl job: {e}")
                
                # Handle pagination
                next_button = await page.query_selector("a.next_page")
                is_disabled = await next_button.get_attribute("class") if next_button else "disabled"
                if not next_button or "disabled" in is_disabled:
                    break
                
                await next_button.click()
                await page.wait_for_load_state("networkidle")
                
        except Exception as e:
            print(f"[ERROR] Cribl scraper failed: {e}")
        finally:
            await self._close_browser(browser)
            
        return jobs 