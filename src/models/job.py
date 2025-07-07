from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import re

@dataclass
class Job:
    """Data model for job postings"""
    title: str
    link: str
    location: str
    company: str
    categories: List[str] = None
    description: Optional[str] = None
    posted_date: Optional[datetime] = None
    salary_range: Optional[str] = None
    
    def __post_init__(self):
        if self.categories is None:
            self.categories = []
    
    def matches_user_preferences(self, user_preferences) -> bool:
        """Check if this job matches user preferences"""
        if not user_preferences:
            return True
            
        # Check categories (whole word match)
        if user_preferences.categories:
            job_title_lower = self.title.lower()
            found = False
            for cat in user_preferences.categories:
                # Use regex word boundary for whole word match
                pattern = r'\b' + re.escape(cat.lower()) + r'\b'
                if re.search(pattern, job_title_lower):
                    found = True
                    break
            if not found:
                return False
        
        # Check locations (case-insensitive substring match)
        if user_preferences.locations:
            job_location_lower = self.location.lower()
            location_matched = False
            for loc in user_preferences.locations:
                loc_lower = loc.lower()
                # Handle "Remote" specially - match common remote variations
                if loc_lower == "remote":
                    if any(remote_term in job_location_lower for remote_term in ["remote", "work from home", "wfh", "virtual"]):
                        location_matched = True
                        break
                elif loc_lower in job_location_lower:
                    location_matched = True
                    break
            if not location_matched:
                return False
        
        # Check companies (case-insensitive exact or substring match)
        if user_preferences.companies:
            company_lower = self.company.lower()
            company_matched = False
            for comp in user_preferences.companies:
                comp_lower = comp.lower()
                # Try exact match first, then substring
                if comp_lower == company_lower or comp_lower in company_lower:
                    company_matched = True
                    break
            if not company_matched:
                return False
        
        return True
    
    def to_dict(self):
        """Convert job to dictionary for storage"""
        return {
            "title": self.title,
            "link": self.link,
            "location": self.location,
            "company": self.company,
            "categories": self.categories,
            "description": self.description,
            "posted_date": self.posted_date.isoformat() if self.posted_date else None,
            "salary_range": self.salary_range
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create job from dictionary"""
        posted_date = None
        if data.get("posted_date"):
            posted_date = datetime.fromisoformat(data["posted_date"])
        
        return cls(
            title=data["title"],
            link=data["link"],
            location=data["location"],
            company=data["company"],
            categories=data.get("categories", []),
            description=data.get("description"),
            posted_date=posted_date,
            salary_range=data.get("salary_range")
        ) 