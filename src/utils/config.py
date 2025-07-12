import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration management for the Job Hunt Buddy Discord Bot
    
    Note: The main entry point for the bot is main.py
    """
    
    # Discord Configuration
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    MAIN_CHANNEL_ID = int(os.getenv("MAIN_CHANNEL_ID", "0"))    # Main channel for job notifications and user joins
    GUIDE_CHANNEL_ID = int(os.getenv("GUIDE_CHANNEL_ID", "0"))  # Channel for posting guide embeds
    
    # File Paths
    SEEN_JOBS_FILE = "data/seen_jobs.json"
    USER_PREFERENCES_FILE = "data/user_preferences.json"  # Will be created if not present
    
    # Scraping Configuration
    SCRAPER_TIMEOUT = 60000  # 60 seconds
    JOB_CHECK_INTERVAL = 7200  # 2 hours in seconds
    
    # Enhanced Job Categories
    DEFAULT_CATEGORIES = [
        # Core Engineering Roles
        "software engineer",
        "frontend",
        "front end", 
        "backend",
        "full stack",
        "fullstack",
        "senior software engineer",
        "junior software engineer",
        "software developer",
        "web developer",
        "mobile developer",
        "ios developer",
        "android developer",
        
        # Specialized Engineering
        "data engineer",
        "data scientist",
        "machine learning engineer",
        "ml engineer",
        "ai engineer",
        "artificial intelligence engineer",
        "devops engineer",
        "site reliability engineer",
        "sre",
        "security engineer",
        "cybersecurity engineer",
        "cloud engineer",
        "infrastructure engineer",
        "platform engineer",
        "reliability engineer",
        "performance engineer",
        "quality assurance engineer",
        "qa engineer",
        "test engineer",
        "automation engineer",
        "embedded engineer",
        "systems engineer",
        "network engineer",
        
        # Product & Design
        "product manager",
        "product owner",
        "technical product manager",
        "ux designer",
        "ui designer",
        "product designer",
        "user experience designer",
        "user interface designer",
        "visual designer",
        "graphic designer",
        "interaction designer",
        
        # Management & Leadership
        "engineering manager",
        "tech lead",
        "technical lead",
        "team lead",
        "project manager",
        "program manager",
        "scrum master",
        "agile coach",
        
        # Business & Marketing
        "marketing manager",
        "digital marketing",
        "growth marketing",
        "content marketing",
        "product marketing",
        "sales engineer",
        "customer success",
        "business analyst",
        "data analyst",
        "analytics engineer",
        
        # Operations & Support
        "customer support",
        "technical support",
        "operations manager",
        "process engineer",
        "business operations",
        
        # Research & Academia
        "research engineer",
        "research scientist",
        "applied scientist",
        "research scientist",
    ]
    
    # Experience Levels
    EXPERIENCE_LEVELS = [
        "entry level",
        "junior",
        "mid level",
        "senior",
        "lead",
        "principal",
        "staff",
        "director",
        "vp",
        "cto",
        "executive"
    ]
    
    # Work Arrangement Types
    WORK_ARRANGEMENTS = [
        "remote",
        "hybrid",
        "onsite",
        "in office",
        "work from home",
        "wfh"
    ]
    
    # Salary Ranges (in thousands USD)
    SALARY_RANGES = [
        "0-50k",
        "50k-75k", 
        "75k-100k",
        "100k-125k",
        "125k-150k",
        "150k-175k",
        "175k-200k",
        "200k-250k",
        "250k-300k",
        "300k+"
    ]
    
    # Notification Frequencies
    NOTIFICATION_FREQUENCIES = [
        "immediate",
        "hourly",
        "daily",
        "weekly",
        "digest"
    ]
    
    # Supported Companies (updated)
    SUPPORTED_COMPANIES = ["discord", "reddit", "monarch", "cribl", "gitlab"]
    
    # Notification Types
    NOTIFICATION_TYPES = [
        "new_jobs",
        "priority_jobs", 
        "salary_alerts",
        "company_alerts",
        "category_alerts",
        "digest_summary"
    ]
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        if not cls.DISCORD_BOT_TOKEN:
            raise ValueError("DISCORD_BOT_TOKEN environment variable is required")
        if cls.MAIN_CHANNEL_ID == 0:
            raise ValueError("MAIN_CHANNEL_ID environment variable is required")
        if cls.GUIDE_CHANNEL_ID == 0:
            print("[WARNING] GUIDE_CHANNEL_ID not set - guide posting features will be limited") 