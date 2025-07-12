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
    
    async def send_job_dump(self, jobs_by_company: dict, channel=None):
        """Send a formatted dump of all current jobs
        
        If there are too many jobs for an embed, generates a .txt file instead.
        """
        if channel is None:
            channel = await self.bot.fetch_channel(self.channel_id)
        if not channel:
            return
        
        # Count total jobs
        total_jobs = sum(len(jobs) for jobs in jobs_by_company.values())
        if total_jobs == 0:
            await channel.send("Sorry, no jobs matched your search. Try broadening your search query or try again once we gather more roles.")
            return
        
        # If we have a lot of jobs, generate a text file
        if total_jobs > 20:  # Threshold for when to use file instead of embed
            await self._send_job_dump_as_file(jobs_by_company, channel)
        else:
            await self._send_job_dump_as_embed(jobs_by_company, channel)
    
    async def _send_job_dump_as_embed(self, jobs_by_company: dict, channel):
        """Send job dump as Discord embed (for smaller job lists)"""
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
    
    async def _send_job_dump_as_file(self, jobs_by_company: dict, channel):
        """Send job dump as a text file (for larger job lists)"""
        import tempfile
        import os
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("🤖 JOB HUNT BUDDY - CURRENT JOB OPENINGS\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total jobs found: {sum(len(jobs) for jobs in jobs_by_company.values())}\n\n")
            
            for company, jobs in jobs_by_company.items():
                if jobs:
                    f.write(f"\n🏢 {company.upper()}\n")
                    f.write("-" * 30 + "\n")
                    for i, job in enumerate(jobs, 1):
                        f.write(f"{i:2d}. {job.title}\n")
                        f.write(f"    Location: {job.location}\n")
                        f.write(f"    Link: {job.link}\n")
                        if job.categories:
                            f.write(f"    Categories: {', '.join(job.categories)}\n")
                        f.write("\n")
                else:
                    f.write(f"\n🏢 {company.upper()}\n")
                    f.write("-" * 30 + "\n")
                    f.write("No jobs found\n\n")
            
            f.write("\n" + "=" * 50 + "\n")
            f.write("Generated by Job Hunt Buddy Discord Bot\n")
            f.write("Use !dumpjobs with filters to narrow results\n")
            f.write("Examples: !dumpjobs category=\"backend\" location=\"Remote\"\n")
        
        try:
            # Send the file
            with open(f.name, 'rb') as file:
                discord_file = discord.File(file, filename=f"job_listings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
                
                embed = discord.Embed(
                    title="📄 Job Listings File",
                    description=f"Found {sum(len(jobs) for jobs in jobs_by_company.values())} jobs across {len(jobs_by_company)} companies.",
                    color=0x0099ff,
                    timestamp=datetime.now()
                )
                embed.add_field(
                    name="📋 Summary", 
                    value="\n".join([f"• {company.title()}: {len(jobs)} jobs" for company, jobs in jobs_by_company.items() if jobs]),
                    inline=False
                )
                embed.add_field(
                    name="💡 Tip",
                    value="Type ex:`!dumpjobs category=\"backend\" location=\"Remote\"` to further filter results on your own.",
                    inline=False
                )
                
                await channel.send(embed=embed, file=discord_file)
                
        finally:
            # Clean up temporary file
            try:
                os.unlink(f.name)
            except:
                pass
    
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
                description=error,
                color=0xff0000,
                timestamp=datetime.now()
            )
            await channel.send(embed=embed)
    
    async def send_cleanup_report(self, removed_jobs: List[Job]):
        """Send a report of removed jobs (optional, for admin monitoring)"""
        if not removed_jobs:
            return
            
        channel = await self.bot.fetch_channel(self.channel_id)
        if not channel:
            return
        
        # Group removed jobs by company
        jobs_by_company = {}
        for job in removed_jobs:
            if job.company not in jobs_by_company:
                jobs_by_company[job.company] = []
            jobs_by_company[job.company].append(job)
        
        embed = discord.Embed(
            title="🧹 Job Database Cleanup Report",
            description=f"Removed {len(removed_jobs)} inactive jobs from the database",
            color=0xffff00,
            timestamp=datetime.now()
        )
        
        for company, jobs in jobs_by_company.items():
            job_list = "\n".join([f"• {job.title}" for job in jobs[:5]])  # Show first 5
            if len(jobs) > 5:
                job_list += f"\n... and {len(jobs) - 5} more"
            embed.add_field(
                name=f"{company.title()} ({len(jobs)} removed)",
                value=job_list,
                inline=False
            )
        
        embed.set_footer(text="These jobs are no longer available on the company's career site")
        await channel.send(embed=embed) 