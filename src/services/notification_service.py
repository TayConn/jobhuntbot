import discord
import asyncio
from typing import List, Optional, Dict
from datetime import datetime, time
from ..models.job import Job
from ..models.user_preferences import UserPreferences
from ..utils.config import Config

class NotificationService:
    """Enhanced service for handling Discord notifications"""
    
    def __init__(self, bot, channel_id: int):
        self.bot = bot
        self.channel_id = channel_id  # This will be MAIN_CHANNEL_ID
        self.pending_notifications: Dict[int, List[Job]] = {}  # user_id -> pending jobs
        self.user_notification_times: Dict[int, time] = {}  # user_id -> notification time
    
    async def send_job_notification(self, job: Job, user_preferences: Optional[UserPreferences] = None):
        """Send a single job notification to Discord"""
        channel = await self.bot.fetch_channel(self.channel_id)
        if not channel:
            print(f"[ERROR] Could not fetch channel {self.channel_id}")
            return
        
        # Determine if this is a priority job
        is_priority = user_preferences and job.is_priority_job(user_preferences)
        priority_score = user_preferences.get_priority_score(user_preferences) if user_preferences else 0
        
        # Create embed with enhanced information
        embed = discord.Embed(
            title=f"{'🔥 PRIORITY: ' if is_priority else ''}{job.title}",
            url=job.link,
            description=f"**Company:** {job.company.title()}\n**Location:** {job.location}",
            color=0xff6b35 if is_priority else 0x00ff00,  # Orange for priority, green for regular
            timestamp=datetime.now()
        )
        
        # Add enhanced fields
        if job.categories:
            embed.add_field(name="Categories", value=", ".join(job.categories), inline=True)
        
        if job.experience_level:
            embed.add_field(name="Experience", value=job.experience_level.title(), inline=True)
        
        if job.work_arrangement:
            embed.add_field(name="Work Type", value=job.work_arrangement.title(), inline=True)
        
        if job.salary_range:
            embed.add_field(name="Salary", value=job.salary_range, inline=True)
        
        if is_priority and priority_score > 0:
            embed.add_field(name="Priority Score", value=f"⭐ {priority_score}", inline=True)
        
        if user_preferences:
            embed.set_footer(text=f"Matched preferences for user {user_preferences.user_id}")
        
        await channel.send(embed=embed)
    
    async def send_personalized_notification(self, user_id: int, jobs: List[Job], user_preferences: UserPreferences):
        """Send personalized notification to a specific user"""
        if not jobs:
            return
        
        try:
            user = await self.bot.fetch_user(user_id)
        except:
            print(f"[ERROR] Could not fetch user {user_id}")
            return
        
        # Sort jobs by priority score
        sorted_jobs = sorted(jobs, key=lambda j: j.get_priority_score(user_preferences), reverse=True)
        
        # Create personalized embed
        embed = discord.Embed(
            title="🎯 Personalized Job Matches",
            description=f"Hi {user.display_name}! Here are jobs that match your preferences:",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        # Add job summary
        priority_jobs = [j for j in jobs if j.is_priority_job(user_preferences)]
        regular_jobs = [j for j in jobs if not j.is_priority_job(user_preferences)]
        
        if priority_jobs:
            embed.add_field(
                name=f"🔥 Priority Jobs ({len(priority_jobs)})",
                value="\n".join([f"• **{job.title}** at {job.company.title()}" for job in priority_jobs[:3]]),
                inline=False
            )
        
        if regular_jobs:
            embed.add_field(
                name=f"📋 Regular Matches ({len(regular_jobs)})",
                value="\n".join([f"• **{job.title}** at {job.company.title()}" for job in regular_jobs[:3]]),
                inline=False
            )
        
        # Add filter summary
        filter_summary = user_preferences.get_filter_summary()
        active_filters = []
        for filter_type, values in filter_summary.items():
            if values:
                active_filters.append(f"{filter_type.title()}: {', '.join(values[:2])}")
        
        if active_filters:
            embed.add_field(
                name="🔍 Active Filters",
                value="\n".join(active_filters[:3]),
                inline=False
            )
        
        embed.set_footer(text=f"Use !dumpjobs to see all jobs or !preferences to update your settings")
        
        try:
            await user.send(embed=embed)
            
            # Send individual job details if there are priority jobs
            if priority_jobs:
                await user.send("🔥 **Priority Job Details:**")
                for job in priority_jobs[:2]:  # Limit to 2 to avoid spam
                    await self.send_job_notification(job, user_preferences)
                    await asyncio.sleep(1)
                    
        except discord.Forbidden:
            print(f"[WARNING] Cannot send DM to user {user_id} - DMs may be disabled")
    
    async def send_bulk_job_notifications(self, jobs: List[Job], user_preferences: Optional[UserPreferences] = None):
        """Send multiple job notifications with enhanced logic"""
        if not jobs:
            await self.send_no_jobs_message()
            return
        
        channel = await self.bot.fetch_channel(self.channel_id)
        if not channel:
            print(f"[ERROR] Could not fetch channel {self.channel_id}")
            return
        
        # If user preferences provided, send personalized notification
        if user_preferences:
            await self.send_personalized_notification(user_preferences.user_id, jobs, user_preferences)
        else:
            # Send individual notifications for each job
            for job in jobs:
                await self.send_job_notification(job, user_preferences)
                await asyncio.sleep(1)  # Small delay to avoid rate limiting
    
    async def send_priority_alert(self, job: Job, user_preferences: UserPreferences):
        """Send immediate priority alert for high-priority jobs"""
        try:
            user = await self.bot.fetch_user(user_preferences.user_id)
        except:
            print(f"[ERROR] Could not fetch user {user_preferences.user_id}")
            return
        
        embed = discord.Embed(
            title="🚨 PRIORITY JOB ALERT!",
            description=f"**{job.title}** at **{job.company.title()}**",
            url=job.link,
            color=0xff0000,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Location", value=job.location, inline=True)
        embed.add_field(name="Priority Score", value=f"⭐ {job.get_priority_score(user_preferences)}", inline=True)
        
        if job.salary_range:
            embed.add_field(name="Salary", value=job.salary_range, inline=True)
        
        embed.set_footer(text="This job matches your priority preferences!")
        
        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            print(f"[WARNING] Cannot send priority alert to user {user_preferences.user_id}")
    
    async def send_daily_digest(self, user_id: int, jobs: List[Job], user_preferences: UserPreferences):
        """Send daily digest of jobs"""
        if not jobs:
            return
        
        try:
            user = await self.bot.fetch_user(user_id)
        except:
            print(f"[ERROR] Could not fetch user {user_id}")
            return
        
        embed = discord.Embed(
            title="📊 Daily Job Digest",
            description=f"Here's your daily summary of {len(jobs)} new job matches:",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        # Group jobs by company
        jobs_by_company = {}
        for job in jobs:
            if job.company not in jobs_by_company:
                jobs_by_company[job.company] = []
            jobs_by_company[job.company].append(job)
        
        # Add company summaries
        for company, company_jobs in list(jobs_by_company.items())[:5]:  # Limit to 5 companies
            job_titles = [job.title for job in company_jobs[:3]]  # Limit to 3 jobs per company
            embed.add_field(
                name=f"🏢 {company.title()} ({len(company_jobs)} jobs)",
                value="\n".join([f"• {title}" for title in job_titles]),
                inline=False
            )
        
        if len(jobs_by_company) > 5:
            embed.add_field(
                name="... and more",
                value=f"{len(jobs_by_company) - 5} more companies with new jobs",
                inline=False
            )
        
        embed.set_footer(text="Use !dumpjobs to see all jobs or !preferences to update your settings")
        
        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            print(f"[WARNING] Cannot send daily digest to user {user_id}")
    
    async def send_weekly_summary(self, user_id: int, jobs: List[Job], user_preferences: UserPreferences):
        """Send weekly summary of jobs"""
        if not jobs:
            return
        
        try:
            user = await self.bot.fetch_user(user_id)
        except:
            print(f"[ERROR] Could not fetch user {user_id}")
            return
        
        embed = discord.Embed(
            title="📈 Weekly Job Summary",
            description=f"Here's your weekly summary of {len(jobs)} job matches:",
            color=0x9932cc,
            timestamp=datetime.now()
        )
        
        # Statistics
        priority_jobs = [j for j in jobs if j.is_priority_job(user_preferences)]
        companies = list(set(job.company for job in jobs))
        categories = []
        for job in jobs:
            categories.extend(job.categories)
        unique_categories = list(set(categories))
        
        embed.add_field(name="📊 Statistics", value=f"""
• Total Jobs: {len(jobs)}
• Priority Jobs: {len(priority_jobs)}
• Companies: {len(companies)}
• Categories: {len(unique_categories)}
        """, inline=False)
        
        # Top companies
        company_counts = {}
        for job in jobs:
            company_counts[job.company] = company_counts.get(job.company, 0) + 1
        
        top_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        if top_companies:
            embed.add_field(
                name="🏆 Top Companies",
                value="\n".join([f"• {company.title()}: {count} jobs" for company, count in top_companies]),
                inline=True
            )
        
        # Top categories
        category_counts = {}
        for category in categories:
            category_counts[category] = category_counts.get(category, 0) + 1
        
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        if top_categories:
            embed.add_field(
                name="🎯 Top Categories",
                value="\n".join([f"• {category.title()}: {count} jobs" for category, count in top_categories]),
                inline=True
            )
        
        embed.set_footer(text="Use !dumpjobs to see all jobs or !preferences to update your settings")
        
        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            print(f"[WARNING] Cannot send weekly summary to user {user_id}")
    
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
                        if job.experience_level:
                            f.write(f"    Experience: {job.experience_level}\n")
                        if job.work_arrangement:
                            f.write(f"    Work Type: {job.work_arrangement}\n")
                        if job.salary_range:
                            f.write(f"    Salary: {job.salary_range}\n")
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
        if preferences.experience_levels:
            embed.add_field(name="Experience Levels", value=", ".join(preferences.experience_levels), inline=True)
        if preferences.work_arrangements:
            embed.add_field(name="Work Arrangements", value=", ".join(preferences.work_arrangements), inline=True)
        if preferences.salary_ranges:
            embed.add_field(name="Salary Ranges", value=", ".join(preferences.salary_ranges), inline=True)
        
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