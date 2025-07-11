import asyncio
from typing import List, Dict
from datetime import datetime
from ..scrapers.discord_scraper import DiscordScraper
from ..scrapers.reddit_scraper import RedditScraper
from ..scrapers.monarch_scraper import MonarchScraper
from ..scrapers.cribl_scraper import CriblScraper
from ..scrapers.gitlab_scraper import GitlabScraper
from ..models.job import Job
from ..models.user_preferences import UserPreferences
from .storage_service import StorageService
from .notification_service import NotificationService
from ..utils.config import Config

class JobMonitor:
    """Main service for monitoring and processing jobs"""
    
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service
        self.storage_service = StorageService()
        self.scrapers = {
            "discord": DiscordScraper(),
            "reddit": RedditScraper(),
            "monarch": MonarchScraper(),
            "cribl": CriblScraper(),
            "gitlab": GitlabScraper()
        }
    
    async def run_job_check(self, user_preferences: UserPreferences = None) -> List[Job]:
        """Run a complete job check across all scrapers"""
        all_new_jobs = []
        
        for company, scraper in self.scrapers.items():
            try:
                print(f"[INFO] Scraping {company} jobs...")
                
                if company == "reddit":
                    jobs = await scraper.scrape_jobs(filter_us_only=True)
                else:
                    jobs = await scraper.scrape_jobs()
                
                # Filter out already seen jobs
                new_jobs = []
                for job in jobs:
                    if not self.storage_service.is_job_seen(job.link):
                        new_jobs.append(job)
                        self.storage_service.add_seen_job(job.link)
                
                # Filter by user preferences if provided
                if user_preferences:
                    filtered_jobs = [
                        job for job in new_jobs 
                        if job.matches_user_preferences(user_preferences)
                    ]
                    new_jobs = filtered_jobs
                
                all_new_jobs.extend(new_jobs)
                print(f"[INFO] Found {len(new_jobs)} new {company} jobs")
                
            except Exception as e:
                print(f"[ERROR] Failed to scrape {company} jobs: {e}")
                await self.notification_service.send_error_message(f"Failed to scrape {company} jobs: {e}")
        
        return all_new_jobs
    
    async def run_full_job_dump(self) -> Dict[str, List[Job]]:
        """Get all current jobs from all scrapers (for dump command)"""
        jobs_by_company = {}
        
        for company, scraper in self.scrapers.items():
            try:
                print(f"[INFO] Scraping {company} jobs for dump...")
                
                if company == "reddit":
                    jobs = await scraper.scrape_jobs(filter_us_only=True)
                else:
                    jobs = await scraper.scrape_jobs()
                
                jobs_by_company[company] = jobs
                print(f"[INFO] Found {len(jobs)} {company} jobs")
                
            except Exception as e:
                print(f"[ERROR] Failed to scrape {company} jobs for dump: {e}")
                jobs_by_company[company] = []
        
        return jobs_by_company
    
    async def monitor_loop(self):
        """Main monitoring loop that runs continuously"""
        print(f"[{datetime.now()}] Starting job monitoring loop...")
        
        while True:
            try:
                # Get all active users
                active_users = self.storage_service.get_all_active_users()
                
                if active_users:
                    # For now, we'll send to all users. In the future, we could
                    # send personalized notifications to each user
                    all_new_jobs = await self.run_job_check()
                    
                    if all_new_jobs:
                        await self.notification_service.send_bulk_job_notifications(all_new_jobs)
                    else:
                        await self.notification_service.send_no_jobs_message()
                else:
                    # No active users, just check for jobs without filtering
                    all_new_jobs = await self.run_job_check()
                    if all_new_jobs:
                        await self.notification_service.send_bulk_job_notifications(all_new_jobs)
                    else:
                        await self.notification_service.send_no_jobs_message()
                
                print(f"[{datetime.now()}] Job check complete. Sleeping for {Config.JOB_CHECK_INTERVAL} seconds.")
                await asyncio.sleep(Config.JOB_CHECK_INTERVAL)
                
            except Exception as e:
                print(f"[ERROR] Error in monitoring loop: {e}")
                await self.notification_service.send_error_message(f"Monitoring loop error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying 