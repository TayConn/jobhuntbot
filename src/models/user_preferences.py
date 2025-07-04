from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class UserPreferences:
    """User preferences for job filtering"""
    user_id: int
    categories: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    companies: List[str] = field(default_factory=list)
    notification_frequency: str = "immediate"  # immediate, daily, weekly
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_category(self, category: str):
        """Add a job category to user preferences"""
        if category.lower() not in [cat.lower() for cat in self.categories]:
            self.categories.append(category)
            self.updated_at = datetime.now()
    
    def remove_category(self, category: str):
        """Remove a job category from user preferences"""
        self.categories = [cat for cat in self.categories if cat.lower() != category.lower()]
        self.updated_at = datetime.now()
    
    def add_location(self, location: str):
        """Add a location to user preferences"""
        if location.lower() not in [loc.lower() for loc in self.locations]:
            self.locations.append(location)
            self.updated_at = datetime.now()
    
    def remove_location(self, location: str):
        """Remove a location from user preferences"""
        self.locations = [loc for loc in self.locations if loc.lower() != location.lower()]
        self.updated_at = datetime.now()
    
    def add_company(self, company: str):
        """Add a company to user preferences"""
        if company.lower() not in [comp.lower() for comp in self.companies]:
            self.companies.append(company)
            self.updated_at = datetime.now()
    
    def remove_company(self, company: str):
        """Remove a company from user preferences"""
        self.companies = [comp for comp in self.companies if comp.lower() != company.lower()]
        self.updated_at = datetime.now()
    
    def to_dict(self):
        """Convert user preferences to dictionary for storage"""
        return {
            "user_id": self.user_id,
            "categories": self.categories,
            "locations": self.locations,
            "companies": self.companies,
            "notification_frequency": self.notification_frequency,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create user preferences from dictionary"""
        created_at = datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now()
        updated_at = datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now()
        
        return cls(
            user_id=data["user_id"],
            categories=data.get("categories", []),
            locations=data.get("locations", []),
            companies=data.get("companies", []),
            notification_frequency=data.get("notification_frequency", "immediate"),
            is_active=data.get("is_active", True),
            created_at=created_at,
            updated_at=updated_at
        ) 