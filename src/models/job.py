from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import re

@dataclass
class Job:
    """Enhanced data model for job postings"""
    title: str
    link: str
    location: str
    company: str
    categories: List[str] = None
    description: Optional[str] = None
    posted_date: Optional[datetime] = None
    salary_range: Optional[str] = None
    
    # Enhanced fields
    experience_level: Optional[str] = None
    work_arrangement: Optional[str] = None  # remote, hybrid, onsite
    salary_min: Optional[int] = None  # Minimum salary in thousands USD
    salary_max: Optional[int] = None  # Maximum salary in thousands USD
    
    def __post_init__(self):
        if self.categories is None:
            self.categories = []
        
        # Auto-detect work arrangement from location if not set
        if not self.work_arrangement:
            self.work_arrangement = self._detect_work_arrangement()
        
        # Auto-detect experience level from title if not set
        if not self.experience_level:
            self.experience_level = self._detect_experience_level()
    
    def _detect_work_arrangement(self) -> Optional[str]:
        """Auto-detect work arrangement from location"""
        location_lower = self.location.lower()
        
        if any(term in location_lower for term in ["remote", "work from home", "wfh", "virtual", "anywhere"]):
            return "remote"
        elif any(term in location_lower for term in ["hybrid", "flexible", "part remote"]):
            return "hybrid"
        elif any(term in location_lower for term in ["onsite", "in office", "on site", "in-person"]):
            return "onsite"
        
        return None
    
    def _detect_experience_level(self) -> Optional[str]:
        """Auto-detect experience level from job title"""
        title_lower = self.title.lower()
        
        # Check for senior/lead/principal/staff levels
        if any(term in title_lower for term in ["senior", "lead", "principal", "staff", "director", "vp", "cto"]):
            return "senior"
        elif any(term in title_lower for term in ["junior", "entry", "associate", "i", "level 1"]):
            return "junior"
        elif any(term in title_lower for term in ["mid", "intermediate", "ii", "level 2"]):
            return "mid level"
        
        return None
    
    def _extract_salary_range(self) -> tuple[Optional[int], Optional[int]]:
        """Extract salary range from description or title"""
        if not self.description:
            return None, None
        
        # Look for salary patterns in description
        desc_lower = self.description.lower()
        
        # Common salary patterns
        patterns = [
            r'\$(\d{1,3}(?:,\d{3})*)\s*-\s*\$(\d{1,3}(?:,\d{3})*)',  # $100k - $150k
            r'\$(\d{1,3}(?:,\d{3})*)\s*to\s*\$(\d{1,3}(?:,\d{3})*)',  # $100k to $150k
            r'(\d{1,3}(?:,\d{3})*)\s*-\s*(\d{1,3}(?:,\d{3})*)\s*k',  # 100k - 150k
            r'(\d{1,3}(?:,\d{3})*)\s*to\s*(\d{1,3}(?:,\d{3})*)\s*k',  # 100k to 150k
        ]
        
        for pattern in patterns:
            match = re.search(pattern, desc_lower)
            if match:
                min_sal = int(match.group(1).replace(',', ''))
                max_sal = int(match.group(2).replace(',', ''))
                return min_sal, max_sal
        
        return None, None
    
    def matches_user_preferences(self, user_preferences) -> bool:
        """Enhanced job matching with new filtering criteria"""
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
        
        # Check experience levels
        if user_preferences.experience_levels and self.experience_level:
            if self.experience_level.lower() not in [lvl.lower() for lvl in user_preferences.experience_levels]:
                return False
        
        # Check work arrangements
        if user_preferences.work_arrangements and self.work_arrangement:
            if self.work_arrangement.lower() not in [arr.lower() for arr in user_preferences.work_arrangements]:
                return False
        
        # Check salary ranges
        if user_preferences.salary_ranges and self.salary_range:
            if self.salary_range not in user_preferences.salary_ranges:
                return False
        
        # Check minimum salary requirement
        if user_preferences.priority_salary_min and self.salary_min:
            if self.salary_min < user_preferences.priority_salary_min:
                return False
        
        return True
    
    def is_priority_job(self, user_preferences) -> bool:
        """Check if this job is a priority job for the user"""
        if not user_preferences or not user_preferences.has_priority_preferences():
            return False
        
        # Check priority companies
        if user_preferences.priority_companies:
            company_lower = self.company.lower()
            for comp in user_preferences.priority_companies:
                if comp.lower() == company_lower:
                    return True
        
        # Check priority categories
        if user_preferences.priority_categories:
            job_title_lower = self.title.lower()
            for cat in user_preferences.priority_categories:
                pattern = r'\b' + re.escape(cat.lower()) + r'\b'
                if re.search(pattern, job_title_lower):
                    return True
        
        # Check priority salary
        if user_preferences.priority_salary_min and self.salary_min:
            if self.salary_min >= user_preferences.priority_salary_min:
                return True
        
        return False
    
    def get_priority_score(self, user_preferences) -> int:
        """Calculate priority score for this job (higher = more priority)"""
        if not user_preferences:
            return 0
        
        score = 0
        
        # Priority company bonus
        if user_preferences.priority_companies:
            company_lower = self.company.lower()
            for comp in user_preferences.priority_companies:
                if comp.lower() == company_lower:
                    score += 10
                    break
        
        # Priority category bonus
        if user_preferences.priority_categories:
            job_title_lower = self.title.lower()
            for cat in user_preferences.priority_categories:
                pattern = r'\b' + re.escape(cat.lower()) + r'\b'
                if re.search(pattern, job_title_lower):
                    score += 5
                    break
        
        # High salary bonus
        if user_preferences.priority_salary_min and self.salary_min:
            if self.salary_min >= user_preferences.priority_salary_min:
                score += 3
        
        # Remote work bonus (common preference)
        if self.work_arrangement == "remote":
            score += 1
        
        return score
    
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
            "salary_range": self.salary_range,
            "experience_level": self.experience_level,
            "work_arrangement": self.work_arrangement,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max
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
            salary_range=data.get("salary_range"),
            experience_level=data.get("experience_level"),
            work_arrangement=data.get("work_arrangement"),
            salary_min=data.get("salary_min"),
            salary_max=data.get("salary_max")
        ) 