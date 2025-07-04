import discord
import asyncio
from typing import List, Optional
from datetime import datetime
from ..models.job import Job
from ..models.user_preferences import UserPreferences

class NotificationService:
    """Service for handling Discord notifications"""
    
    def __init__(self, bot, channel_id: int):
        self.bot = bot
        self.channel_id = channel_id  # This will be MAIN_CHANNEL_ID
    
    async def send_job_notification(self, job: Job, user_preferences: Optional[UserPreferences] = None):
        """Send a single job notification to Discord"""
        channel = await self.bot.fetch_channel(self.channel_id)
        if not channel:
            print(f"[ERROR] Could not fetch channel {self.channel_id}")
            return
        
        # Create embed for better formatting
        embed = discord.Embed(
            title=f"📢 New Job: {job.title}",
            url=job.link,
            description=f"**Company:** {job.company.title()}\n**Location:** {job.location}",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        
        if job.categories:
            embed.add_field(name="Categories", value=", ".join(job.categories), inline=True)
        
        if user_preferences:
            embed.set_footer(text=f"Matched preferences for user {user_preferences.user_id}")
        
        await channel.send(embed=embed)
    
    async def send_bulk_job_notifications(self, jobs: List[Job], user_preferences: Optional[UserPreferences] = None):
        """Send multiple job notifications"""
        if not jobs:
            await self.send_no_jobs_message()
            return
        
        channel = await self.bot.fetch_channel(self.channel_id)
        if not channel:
            print(f"[ERROR] Could not fetch channel {self.channel_id}")
            return
        
        # Send individual notifications for each job
        for job in jobs:
            await self.send_job_notification(job, user_preferences)
            await asyncio.sleep(1)  # Small delay to avoid rate limiting
    
    async def send_no_jobs_message(self):
        """Send message when no new jobs are found"""
        channel = await self.bot.fetch_channel(self.channel_id)
        if channel:
            embed = discord.Embed(
                title="🤖 Job Check Complete",
                description="No new job listings found this time!",
                color=0xffff00,
                timestamp=datetime.now()
            )
            await channel.send(embed=embed)
    
    async def send_job_dump(self, jobs_by_company: dict):
        """Send a formatted dump of all current jobs"""
        channel = await self.bot.fetch_channel(self.channel_id)
        if not channel:
            return
        
        embed = discord.Embed(
            title="🧾 Current Job Openings",
            description="Here are all the current job listings:",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        for company, jobs in jobs_by_company.items():
            if jobs:
                job_list = "\n".join([
                    f"• **{job.title}** — {job.location}\n  {job.link}"
                    for job in jobs[:5]  # Limit to 5 jobs per company to avoid embed limits
                ])
                if len(jobs) > 5:
                    job_list += f"\n... and {len(jobs) - 5} more"
                embed.add_field(name=company.title(), value=job_list, inline=False)
            else:
                embed.add_field(name=company.title(), value="No jobs found", inline=False)
        
        await channel.send(embed=embed)
    
    async def send_user_preferences_updated(self, user_id: int, preferences: UserPreferences):
        """Send confirmation when user preferences are updated"""
        channel = await self.bot.fetch_channel(self.channel_id)
        if not channel:
            return
        
        embed = discord.Embed(
            title="⚙️ Preferences Updated",
            description=f"Your job preferences have been updated!",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        
        if preferences.categories:
            embed.add_field(name="Categories", value=", ".join(preferences.categories), inline=True)
        if preferences.locations:
            embed.add_field(name="Locations", value=", ".join(preferences.locations), inline=True)
        if preferences.companies:
            embed.add_field(name="Companies", value=", ".join(preferences.companies), inline=True)
        
        embed.set_footer(text=f"User ID: {user_id}")
        await channel.send(embed=embed)
    
    async def send_error_message(self, error: str):
        """Send error message to Discord"""
        channel = await self.bot.fetch_channel(self.channel_id)
        if channel:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {error}",
                color=0xff0000,
                timestamp=datetime.now()
            )
            await channel.send(embed=embed) 