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
    
    # Default Job Categories
    DEFAULT_CATEGORIES = [
        "software engineer",
        "frontend",
        "front end", 
        "backend",
        "full stack",
        "product manager",
        "marketing",
        "design",
        "data scientist",
        "devops",
        "qa",
        "test engineer",
        "security",
        "sre",
        "devsecops",
        "devops engineer",
        "devops engineer",
    ]
    
    # Supported Companies
    SUPPORTED_COMPANIES = ["discord", "reddit", "monarch"]
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        if not cls.DISCORD_BOT_TOKEN:
            raise ValueError("DISCORD_BOT_TOKEN environment variable is required")
        if cls.MAIN_CHANNEL_ID == 0:
            raise ValueError("MAIN_CHANNEL_ID environment variable is required")
        if cls.GUIDE_CHANNEL_ID == 0:
            print("[WARNING] GUIDE_CHANNEL_ID not set - guide posting features will be limited") 