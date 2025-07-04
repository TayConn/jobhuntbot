from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

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
            
        # Check categories
        if user_preferences.categories:
            job_title_lower = self.title.lower()
            if not any(cat.lower() in job_title_lower for cat in user_preferences.categories):
                return False
        
        # Check locations
        if user_preferences.locations:
            job_location_lower = self.location.lower()
            if not any(loc.lower() in job_location_lower for loc in user_preferences.locations):
                return False
        
        # Check companies
        if user_preferences.companies:
            company_lower = self.company.lower()
            if not any(comp.lower() in company_lower for comp in user_preferences.companies):
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