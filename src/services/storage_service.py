import json
import os
from datetime import datetime
from typing import Set, Dict, List
from ..models.job import Job
from ..models.user_preferences import UserPreferences
from ..utils.config import Config

class StorageService:
    """Service for managing job and user preference storage"""
    
    def __init__(self):
        self.seen_jobs_file = Config.SEEN_JOBS_FILE
        self.user_preferences_file = Config.USER_PREFERENCES_FILE
        self.active_jobs_file = "data/active_jobs.json"  # New file for tracking active jobs
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        os.makedirs(os.path.dirname(self.seen_jobs_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.user_preferences_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.active_jobs_file), exist_ok=True)
    
    def load_seen_jobs(self) -> Set[str]:
        """Load seen job URLs from file"""
        try:
            with open(self.seen_jobs_file, "r") as f:
                return set(json.load(f))
        except FileNotFoundError:
            return set()
    
    def save_seen_jobs(self, seen_jobs: Set[str]):
        """Save seen job URLs to file"""
        with open(self.seen_jobs_file, "w") as f:
            json.dump(list(seen_jobs), f)
    
    def add_seen_job(self, job_url: str):
        """Add a job URL to seen jobs"""
        seen_jobs = self.load_seen_jobs()
        seen_jobs.add(job_url)
        self.save_seen_jobs(seen_jobs)
    
    def is_job_seen(self, job_url: str) -> bool:
        """Check if a job URL has been seen before"""
        seen_jobs = self.load_seen_jobs()
        return job_url in seen_jobs
    
    def load_active_jobs(self) -> Dict[str, Job]:
        """Load all currently active jobs from file"""
        try:
            with open(self.active_jobs_file, "r") as f:
                data = json.load(f)
                return {
                    job_url: Job.from_dict(job_data)
                    for job_url, job_data in data.items()
                }
        except FileNotFoundError:
            return {}
    
    def save_active_jobs(self, active_jobs: Dict[str, Job]):
        """Save all currently active jobs to file"""
        data = {
            job_url: job.to_dict()
            for job_url, job in active_jobs.items()
        }
        with open(self.active_jobs_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def update_active_jobs(self, company: str, current_jobs: List[Job]):
        """Update active jobs for a company and return removed jobs"""
        active_jobs = self.load_active_jobs()
        
        # Get current job URLs for this company
        current_job_urls = {job.link for job in current_jobs}
        
        # Find jobs to remove (jobs from this company that are no longer active)
        jobs_to_remove = []
        jobs_to_delete = []
        for job_url, job in active_jobs.items():
            if job.company.lower() == company.lower() and job_url not in current_job_urls:
                jobs_to_remove.append(job)
                jobs_to_delete.append(job_url)
        
        # Remove jobs after iteration
        for job_url in jobs_to_delete:
            del active_jobs[job_url]
        
        # Add new jobs to active jobs
        for job in current_jobs:
            active_jobs[job.link] = job
        
        # Save updated active jobs
        self.save_active_jobs(active_jobs)
        
        return jobs_to_remove
    
    def cleanup_inactive_jobs(self, all_current_jobs: Dict[str, List[Job]]) -> List[Job]:
        """Clean up jobs that are no longer active and return removed jobs"""
        active_jobs = self.load_active_jobs()
        
        # Get all current job URLs
        current_job_urls = set()
        for jobs in all_current_jobs.values():
            current_job_urls.update(job.link for job in jobs)
        
        # Find jobs to remove
        jobs_to_remove = []
        jobs_to_delete = []
        for job_url, job in active_jobs.items():
            if job_url not in current_job_urls:
                jobs_to_remove.append(job)
                jobs_to_delete.append(job_url)
        
        # Remove jobs after iteration
        for job_url in jobs_to_delete:
            del active_jobs[job_url]
        
        # Save updated active jobs
        self.save_active_jobs(active_jobs)
        
        return jobs_to_remove
    
    def load_user_preferences(self) -> Dict[int, UserPreferences]:
        """Load all user preferences from file"""
        try:
            with open(self.user_preferences_file, "r") as f:
                data = json.load(f)
                # Migrate any dicts to UserPreferences
                migrated = False
                result = {}
                for user_id, pref_data in data.items():
                    if isinstance(pref_data, dict):
                        result[int(user_id)] = UserPreferences.from_dict(pref_data)
                        migrated = True
                    else:
                        result[int(user_id)] = pref_data
                if migrated:
                    # Save back the migrated data
                    self.save_user_preferences(result)
                return result
        except FileNotFoundError:
            return {}
    
    def save_user_preferences(self, user_preferences: Dict[int, UserPreferences]):
        """Save all user preferences to file"""
        data = {
            str(user_id): pref.to_dict()
            for user_id, pref in user_preferences.items()
        }
        with open(self.user_preferences_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def get_user_preferences(self, user_id: int) -> UserPreferences:
        """Get preferences for a specific user"""
        all_preferences = self.load_user_preferences()
        return all_preferences.get(user_id, UserPreferences(user_id=user_id))
    
    def save_user_preferences(self, user_preferences: UserPreferences):
        """Save preferences for a specific user"""
        all_preferences = self.load_user_preferences()
        all_preferences[user_preferences.user_id] = user_preferences
        self.save_user_preferences(all_preferences)
    
    def update_user_preferences(self, user_id: int, **kwargs):
        """Update user preferences with new values"""
        preferences = self.get_user_preferences(user_id)
        
        for key, value in kwargs.items():
            if hasattr(preferences, key):
                setattr(preferences, key, value)
        
        preferences.updated_at = datetime.now()
        self.save_user_preferences(preferences)
        return preferences
    
    def get_all_active_users(self) -> List[int]:
        """Get list of all active user IDs"""
        all_preferences = self.load_user_preferences()
        return [
            user_id for user_id, pref in all_preferences.items()
            if pref.is_active
        ] 