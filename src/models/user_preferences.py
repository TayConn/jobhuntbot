from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set
from datetime import datetime, time
from ..utils.config import Config

@dataclass
class UserPreferences:
    """Enhanced user preferences for job filtering and notifications"""
    user_id: int
    categories: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    companies: List[str] = field(default_factory=list)
    
    # Enhanced filtering options
    experience_levels: List[str] = field(default_factory=list)
    salary_ranges: List[str] = field(default_factory=list)
    work_arrangements: List[str] = field(default_factory=list)
    
    # Notification preferences
    notification_frequency: str = "immediate"  # immediate, hourly, daily, weekly, digest
    notification_types: List[str] = field(default_factory=lambda: ["new_jobs"])
    notification_time: Optional[time] = None  # For scheduled notifications
    notification_timezone: str = "UTC"
    
    # Priority settings
    priority_companies: List[str] = field(default_factory=list)
    priority_categories: List[str] = field(default_factory=list)
    priority_salary_min: Optional[int] = None  # Minimum salary in thousands
    
    # Status
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Category management
    def add_category(self, category: str):
        """Add a job category to user preferences"""
        if category.lower() not in [cat.lower() for cat in self.categories]:
            self.categories.append(category)
            self.updated_at = datetime.now()
    
    def remove_category(self, category: str):
        """Remove a job category from user preferences"""
        self.categories = [cat for cat in self.categories if cat.lower() != category.lower()]
        self.updated_at = datetime.now()
    
    # Location management
    def add_location(self, location: str):
        """Add a location to user preferences"""
        if location.lower() not in [loc.lower() for loc in self.locations]:
            self.locations.append(location)
            self.updated_at = datetime.now()
    
    def remove_location(self, location: str):
        """Remove a location from user preferences"""
        self.locations = [loc for loc in self.locations if loc.lower() != location.lower()]
        self.updated_at = datetime.now()
    
    # Company management
    def add_company(self, company: str):
        """Add a company to user preferences"""
        if company.lower() not in [comp.lower() for comp in self.companies]:
            self.companies.append(company)
            self.updated_at = datetime.now()
    
    def remove_company(self, company: str):
        """Remove a company from user preferences"""
        self.companies = [comp for comp in self.companies if comp.lower() != company.lower()]
        self.updated_at = datetime.now()
    
    # Experience level management
    def add_experience_level(self, level: str):
        """Add an experience level to user preferences"""
        if level.lower() not in [lvl.lower() for lvl in self.experience_levels]:
            self.experience_levels.append(level)
            self.updated_at = datetime.now()
    
    def remove_experience_level(self, level: str):
        """Remove an experience level from user preferences"""
        self.experience_levels = [lvl for lvl in self.experience_levels if lvl.lower() != level.lower()]
        self.updated_at = datetime.now()
    
    # Salary range management
    def add_salary_range(self, salary_range: str):
        """Add a salary range to user preferences"""
        if salary_range not in self.salary_ranges:
            self.salary_ranges.append(salary_range)
            self.updated_at = datetime.now()
    
    def remove_salary_range(self, salary_range: str):
        """Remove a salary range from user preferences"""
        self.salary_ranges = [sr for sr in self.salary_ranges if sr != salary_range]
        self.updated_at = datetime.now()
    
    # Work arrangement management
    def add_work_arrangement(self, arrangement: str):
        """Add a work arrangement to user preferences"""
        if arrangement.lower() not in [arr.lower() for arr in self.work_arrangements]:
            self.work_arrangements.append(arrangement)
            self.updated_at = datetime.now()
    
    def remove_work_arrangement(self, arrangement: str):
        """Remove a work arrangement from user preferences"""
        self.work_arrangements = [arr for arr in self.work_arrangements if arr.lower() != arrangement.lower()]
        self.updated_at = datetime.now()
    
    # Priority management
    def add_priority_company(self, company: str):
        """Add a priority company"""
        if company.lower() not in [comp.lower() for comp in self.priority_companies]:
            self.priority_companies.append(company)
            self.updated_at = datetime.now()
    
    def remove_priority_company(self, company: str):
        """Remove a priority company"""
        self.priority_companies = [comp for comp in self.priority_companies if comp.lower() != company.lower()]
        self.updated_at = datetime.now()
    
    def add_priority_category(self, category: str):
        """Add a priority category"""
        if category.lower() not in [cat.lower() for cat in self.priority_categories]:
            self.priority_categories.append(category)
            self.updated_at = datetime.now()
    
    def remove_priority_category(self, category: str):
        """Remove a priority category"""
        self.priority_categories = [cat for cat in self.priority_categories if cat.lower() != category.lower()]
        self.updated_at = datetime.now()
    
    # Notification management
    def add_notification_type(self, notification_type: str):
        """Add a notification type"""
        if notification_type not in self.notification_types:
            self.notification_types.append(notification_type)
            self.updated_at = datetime.now()
    
    def remove_notification_type(self, notification_type: str):
        """Remove a notification type"""
        self.notification_types = [nt for nt in self.notification_types if nt != notification_type]
        self.updated_at = datetime.now()
    
    def set_notification_time(self, hour: int, minute: int = 0):
        """Set notification time for scheduled notifications"""
        self.notification_time = time(hour, minute)
        self.updated_at = datetime.now()
    
    def set_priority_salary_min(self, salary_min: int):
        """Set minimum priority salary in thousands USD"""
        self.priority_salary_min = salary_min
        self.updated_at = datetime.now()
    
    # Utility methods
    def has_any_preferences(self) -> bool:
        """Check if user has any filtering preferences set"""
        return bool(
            self.categories or 
            self.locations or 
            self.companies or
            self.experience_levels or
            self.salary_ranges or
            self.work_arrangements
        )
    
    def has_priority_preferences(self) -> bool:
        """Check if user has any priority preferences set"""
        return bool(
            self.priority_companies or
            self.priority_categories or
            self.priority_salary_min is not None
        )
    
    def get_filter_summary(self) -> Dict[str, List[str]]:
        """Get a summary of all active filters"""
        return {
            "categories": self.categories,
            "locations": self.locations,
            "companies": self.companies,
            "experience_levels": self.experience_levels,
            "salary_ranges": self.salary_ranges,
            "work_arrangements": self.work_arrangements
        }
    
    def to_dict(self):
        """Convert user preferences to dictionary for storage"""
        return {
            "user_id": self.user_id,
            "categories": self.categories,
            "locations": self.locations,
            "companies": self.companies,
            "experience_levels": self.experience_levels,
            "salary_ranges": self.salary_ranges,
            "work_arrangements": self.work_arrangements,
            "notification_frequency": self.notification_frequency,
            "notification_types": self.notification_types,
            "notification_time": self.notification_time.isoformat() if self.notification_time else None,
            "notification_timezone": self.notification_timezone,
            "priority_companies": self.priority_companies,
            "priority_categories": self.priority_categories,
            "priority_salary_min": self.priority_salary_min,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create user preferences from dictionary"""
        created_at = datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now()
        updated_at = datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now()
        
        # Parse notification time
        notification_time = None
        if data.get("notification_time"):
            try:
                notification_time = time.fromisoformat(data["notification_time"])
            except:
                pass
        
        return cls(
            user_id=data["user_id"],
            categories=data.get("categories", []),
            locations=data.get("locations", []),
            companies=data.get("companies", []),
            experience_levels=data.get("experience_levels", []),
            salary_ranges=data.get("salary_ranges", []),
            work_arrangements=data.get("work_arrangements", []),
            notification_frequency=data.get("notification_frequency", "immediate"),
            notification_types=data.get("notification_types", ["new_jobs"]),
            notification_time=notification_time,
            notification_timezone=data.get("notification_timezone", "UTC"),
            priority_companies=data.get("priority_companies", []),
            priority_categories=data.get("priority_categories", []),
            priority_salary_min=data.get("priority_salary_min"),
            is_active=data.get("is_active", True),
            created_at=created_at,
            updated_at=updated_at
        ) 