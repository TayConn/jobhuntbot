from typing import List
from playwright.async_api import Page
from .base_scraper import BaseScraper
from ..models.job import Job

class DiscordScraper(BaseScraper):
    """Scraper for Discord jobs"""
    
    def __init__(self):
        super().__init__("discord")
        self.base_url = "https://discord.com/careers"
    
    async def scrape_jobs(self) -> List[Job]:
        """Scrape jobs from Discord careers page"""
        jobs = []
        browser, page = await self._get_browser_page()
        
        try:
            await page.goto(self.base_url, timeout=self.timeout)
            await page.wait_for_load_state("networkidle")
            
            job_cards = await page.query_selector_all("a.job-item.w-inline-block")
            
            for card in job_cards:
                try:
                    title_elem = await card.query_selector("h3")
                    location_elem = await card.query_selector("p")
                    href = await card.get_attribute("href")
                    
                    title = await title_elem.inner_text() if title_elem else "N/A"
                    location = await location_elem.inner_text() if location_elem else "N/A"
                    link = f"https://discord.com{href}" if href else ""
                    
                    if title != "N/A" and link:
                        categories = self._extract_categories_from_title(title)
                        job = self._create_job(title, link, location, categories)
                        jobs.append(job)
                        
                except Exception as e:
                    print(f"[DEBUG] Failed to parse a Discord job card: {e}")
                    
        except Exception as e:
            print(f"[ERROR] Discord scraper failed: {e}")
        finally:
            await self._close_browser(browser)
            
        return jobs 