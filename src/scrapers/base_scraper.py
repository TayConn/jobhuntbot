from abc import ABC, abstractmethod
from typing import List
from playwright.async_api import async_playwright, Page, Browser
from ..models.job import Job
from ..utils.config import Config

class BaseScraper(ABC):
    """Abstract base class for job scrapers"""
    
    def __init__(self, company_name: str):
        self.company_name = company_name
        self.timeout = Config.SCRAPER_TIMEOUT
    
    @abstractmethod
    async def scrape_jobs(self) -> List[Job]:
        """Scrape jobs from the company's career page"""
        pass
    
    async def _get_browser_page(self) -> tuple[Browser, Page]:
        """Get a browser and page instance for scraping"""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        return browser, page
    
    async def _close_browser(self, browser: Browser):
        """Close the browser instance"""
        await browser.close()
    
    def _create_job(self, title: str, link: str, location: str, 
                   categories: List[str] = None, description: str = None,
                   salary_range: str = None) -> Job:
        """Create a Job instance with standard fields"""
        return Job(
            title=title.strip(),
            link=link.strip(),
            location=location.strip(),
            company=self.company_name,
            categories=categories or [],
            description=description,
            salary_range=salary_range
        )
    
    def _extract_categories_from_title(self, title: str) -> List[str]:
        """Extract job categories from the job title"""
        title_lower = title.lower()
        categories = []
        
        # Define category keywords
        category_keywords = {
            "software engineer": ["software engineer", "software developer", "developer"],
            "frontend": ["frontend", "front end", "front-end", "ui", "react", "vue", "angular"],
            "backend": ["backend", "back end", "back-end", "api", "server"],
            "full stack": ["full stack", "fullstack", "full-stack"],
            "devops": ["devops", "sre", "site reliability", "infrastructure"],
            "data": ["data scientist", "data engineer", "analyst", "ml", "machine learning"],
            "product": ["product manager", "product owner", "pm"],
            "design": ["designer", "ux", "ui/ux", "visual designer"],
            "marketing": ["marketing", "growth", "seo", "content"],
            "qa": ["qa", "quality assurance", "test engineer", "testing"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                categories.append(category)
        
        return categories 