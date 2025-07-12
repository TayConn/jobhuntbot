import discord
from discord.ext import commands
from typing import List
from ..services.job_monitor import JobMonitor
from ..services.storage_service import StorageService
from ..services.notification_service import NotificationService
from ..models.user_preferences import UserPreferences
from ..utils.config import Config
from .interactive_ui import InteractiveUI

class JobBotCommands(commands.Cog):
    """Discord bot commands for job hunting"""
    
    def __init__(self, bot, job_monitor: JobMonitor, 
                 notification_service: NotificationService):
        self.bot = bot
        self.job_monitor = job_monitor
        self.notification_service = notification_service
        self.storage_service = StorageService()
        self.interactive_ui = InteractiveUI(bot)
    
    @commands.command(name="checknow")
    async def check_now(self, ctx):
        """Manually trigger a job check"""
        await ctx.send("🔍 Checking for new jobs now...")
        
        try:
            # Get user preferences if they exist
            user_prefs = self.storage_service.get_user_preferences(ctx.author.id)
            
            new_jobs = await self.job_monitor.run_job_check(user_prefs)
            
            if new_jobs:
                await self.notification_service.send_bulk_job_notifications(new_jobs, user_prefs)
            else:
                await ctx.send("✅ No new jobs found!")
                
        except Exception as e:
            await ctx.send(f"❌ Error checking jobs: {e}")
    
    @commands.command(name="dumpjobs")
    async def dump_jobs(self, ctx, *, filters: str = None):
        """Get all current job listings with optional filters
        
        Usage examples:
        !dumpjobs                                    - Interactive filter selection
        !dumpjobs category="backend"                 - Filter by category
        !dumpjobs location="Remote"                  - Filter by location  
        !dumpjobs company="discord"                  - Filter by company
        !dumpjobs experience="senior"                - Filter by experience level
        !dumpjobs salary="100k-150k"                 - Filter by salary range
        !dumpjobs work="remote"                      - Filter by work arrangement
        !dumpjobs category="backend" location="Remote" experience="senior" - Multiple filters
        """
        if not filters:
            # Start interactive session
            await self.interactive_ui.start_dumpjobs_session(ctx)
            return
        
        await ctx.send("🕵️ Scraping all current job listings (this may take a few seconds)...")
        
        try:
            # Parse filters if provided
            filter_prefs = None
            if filters:
                filter_prefs = self._parse_dump_filters(filters)
                if filter_prefs:
                    filter_text = []
                    if filter_prefs.categories:
                        filter_text.append(f"Categories: {', '.join(filter_prefs.categories)}")
                    if filter_prefs.locations:
                        filter_text.append(f"Locations: {', '.join(filter_prefs.locations)}")
                    if filter_prefs.companies:
                        filter_text.append(f"Companies: {', '.join(filter_prefs.companies)}")
                    if filter_prefs.experience_levels:
                        filter_text.append(f"Experience: {', '.join(filter_prefs.experience_levels)}")
                    if filter_prefs.salary_ranges:
                        filter_text.append(f"Salary: {', '.join(filter_prefs.salary_ranges)}")
                    if filter_prefs.work_arrangements:
                        filter_text.append(f"Work Type: {', '.join(filter_prefs.work_arrangements)}")
                    
                    await ctx.send(f"🔍 Applying filters: {', '.join(filter_text)}")
            
            jobs_by_company = await self.job_monitor.run_full_job_dump()
            
            # Apply filters if provided
            if filter_prefs:
                filtered_jobs_by_company = {}
                for company, jobs in jobs_by_company.items():
                    filtered_jobs = [
                        job for job in jobs 
                        if job.matches_user_preferences(filter_prefs)
                    ]
                    if filtered_jobs:
                        filtered_jobs_by_company[company] = filtered_jobs
                jobs_by_company = filtered_jobs_by_company
            
            # Send the results
            await self.notification_service.send_job_dump(jobs_by_company, ctx.channel)
            
        except Exception as e:
            await ctx.send(f"❌ Error dumping jobs: {e}")
    
    def _parse_dump_filters(self, filters_str: str) -> UserPreferences:
        """Parse filter string into UserPreferences object
        
        Expected format: category="backend, frontend" location="Remote" experience="senior" salary="100k-150k"
        """
        try:
            # Create a temporary UserPreferences object for filtering
            filter_prefs = UserPreferences(user_id=0)  # user_id doesn't matter for filtering
            
            # Split by spaces but respect quoted strings
            import re
            # This regex splits on spaces but keeps quoted strings together
            parts = re.findall(r'(\w+)="([^"]*)"', filters_str)
            
            for key, value in parts:
                if key.lower() == "category":
                    # Split by comma and strip whitespace
                    categories = [cat.strip() for cat in value.split(",")]
                    filter_prefs.categories.extend(categories)
                elif key.lower() == "location":
                    locations = [loc.strip() for loc in value.split(",")]
                    filter_prefs.locations.extend(locations)
                elif key.lower() == "company":
                    companies = [comp.strip() for comp in value.split(",")]
                    filter_prefs.companies.extend(companies)
                elif key.lower() == "experience":
                    experience_levels = [exp.strip() for exp in value.split(",")]
                    filter_prefs.experience_levels.extend(experience_levels)
                elif key.lower() == "salary":
                    salary_ranges = [sal.strip() for sal in value.split(",")]
                    filter_prefs.salary_ranges.extend(salary_ranges)
                elif key.lower() == "work":
                    work_arrangements = [work.strip() for work in value.split(",")]
                    filter_prefs.work_arrangements.extend(work_arrangements)
            
            return filter_prefs if filter_prefs.has_any_preferences() else None
            
        except Exception as e:
            print(f"[ERROR] Failed to parse dump filters: {e}")
            return None
    
    @commands.command(name="subscribe")
    async def subscribe(self, ctx, category: str = None):
        """Subscribe to job categories. Usage: !subscribe [category] or !subscribe to see available categories"""
        if not category:
            # Start interactive session
            await self.interactive_ui.start_subscribe_session(ctx)
            return
        
        # Add category to user preferences
        user_prefs = self.storage_service.get_user_preferences(ctx.author.id)
        user_prefs.add_category(category)
        self.storage_service.save_user_preferences(user_prefs)
        
        embed = discord.Embed(
            title="✅ Subscribed!",
            description=f"You're now subscribed to **{category}** jobs",
            color=0x00ff00
        )
        embed.add_field(name="Your Categories", value=", ".join(user_prefs.categories) or "None")
        await ctx.send(embed=embed)
    
    @commands.command(name="unsubscribe")
    async def unsubscribe(self, ctx, category: str = None):
        """Unsubscribe from job categories. Usage: !unsubscribe [category] or !unsubscribe to see your subscriptions"""
        if not category:
            # Start interactive session
            await self.interactive_ui.start_unsubscribe_session(ctx)
            return
        
        user_prefs = self.storage_service.get_user_preferences(ctx.author.id)
        
        # Remove category from user preferences
        user_prefs.remove_category(category)
        self.storage_service.save_user_preferences(user_prefs)
        
        embed = discord.Embed(
            title="✅ Unsubscribed!",
            description=f"You're no longer subscribed to **{category}** jobs",
            color=0x00ff00
        )
        embed.add_field(name="Your Categories", value=", ".join(user_prefs.categories) or "None")
        await ctx.send(embed=embed)
    
    @commands.command(name="preferences")
    async def show_preferences(self, ctx):
        """Show your current job preferences"""
        user_prefs = self.storage_service.get_user_preferences(ctx.author.id)
        
        embed = discord.Embed(
            title="⚙️ Your Job Preferences",
            description=f"User ID: {ctx.author.id}",
            color=0x0099ff
        )
        
        embed.add_field(
            name="Categories", 
            value=", ".join(user_prefs.categories) if user_prefs.categories else "None",
            inline=False
        )
        embed.add_field(
            name="Locations", 
            value=", ".join(user_prefs.locations) if user_prefs.locations else "None",
            inline=False
        )
        embed.add_field(
            name="Companies", 
            value=", ".join(user_prefs.companies) if user_prefs.companies else "None",
            inline=False
        )
        embed.add_field(
            name="Experience Levels", 
            value=", ".join(user_prefs.experience_levels) if user_prefs.experience_levels else "None",
            inline=False
        )
        embed.add_field(
            name="Salary Ranges", 
            value=", ".join(user_prefs.salary_ranges) if user_prefs.salary_ranges else "None",
            inline=False
        )
        embed.add_field(
            name="Work Arrangements", 
            value=", ".join(user_prefs.work_arrangements) if user_prefs.work_arrangements else "None",
            inline=False
        )
        embed.add_field(
            name="Notification Frequency", 
            value=user_prefs.notification_frequency,
            inline=False
        )
        embed.add_field(
            name="Priority Companies", 
            value=", ".join(user_prefs.priority_companies) if user_prefs.priority_companies else "None",
            inline=False
        )
        embed.add_field(
            name="Priority Categories", 
            value=", ".join(user_prefs.priority_categories) if user_prefs.priority_categories else "None",
            inline=False
        )
        embed.add_field(
            name="Status", 
            value="Active" if user_prefs.is_active else "Inactive",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="addlocation")
    async def add_location(self, ctx, location: str = None):
        """Add a location preference. Usage: !addlocation [location] or !addlocation for interactive selection"""
        if not location:
            # Start interactive session
            await self.interactive_ui.start_addlocation_session(ctx)
            return
        
        user_prefs = self.storage_service.get_user_preferences(ctx.author.id)
        user_prefs.add_location(location)
        self.storage_service.save_user_preferences(user_prefs)
        
        embed = discord.Embed(
            title="📍 Location Added!",
            description=f"Added **{location}** to your location preferences",
            color=0x00ff00
        )
        embed.add_field(name="Your Locations", value=", ".join(user_prefs.locations))
        await ctx.send(embed=embed)
    
    @commands.command(name="addcompany")
    async def add_company(self, ctx, company: str = None):
        """Add a company preference. Usage: !addcompany [company] or !addcompany for interactive selection"""
        if not company:
            # Start interactive session
            await self.interactive_ui.start_addcompany_session(ctx)
            return
        
        user_prefs = self.storage_service.get_user_preferences(ctx.author.id)
        user_prefs.add_company(company)
        self.storage_service.save_user_preferences(user_prefs)
        
        embed = discord.Embed(
            title="🏢 Company Added!",
            description=f"Added **{company}** to your company preferences",
            color=0x00ff00
        )
        embed.add_field(name="Your Companies", value=", ".join(user_prefs.companies))
        await ctx.send(embed=embed)
    
    # New enhanced filtering commands
    @commands.command(name="addexperience")
    async def add_experience(self, ctx, experience: str = None):
        """Add an experience level preference. Usage: !addexperience [level] or !addexperience for interactive selection"""
        if not experience:
            # Start interactive session
            await self.interactive_ui.start_addexperience_session(ctx)
            return
        
        user_prefs = self.storage_service.get_user_preferences(ctx.author.id)
        user_prefs.add_experience_level(experience)
        self.storage_service.save_user_preferences(user_prefs)
        
        embed = discord.Embed(
            title="👨‍💼 Experience Level Added!",
            description=f"Added **{experience}** to your experience level preferences",
            color=0x00ff00
        )
        embed.add_field(name="Your Experience Levels", value=", ".join(user_prefs.experience_levels))
        await ctx.send(embed=embed)
    
    @commands.command(name="addsalary")
    async def add_salary(self, ctx, salary_range: str = None):
        """Add a salary range preference. Usage: !addsalary [range] or !addsalary for interactive selection"""
        if not salary_range:
            # Start interactive session
            await self.interactive_ui.start_addsalary_session(ctx)
            return
        
        user_prefs = self.storage_service.get_user_preferences(ctx.author.id)
        user_prefs.add_salary_range(salary_range)
        self.storage_service.save_user_preferences(user_prefs)
        
        embed = discord.Embed(
            title="💰 Salary Range Added!",
            description=f"Added **{salary_range}** to your salary range preferences",
            color=0x00ff00
        )
        embed.add_field(name="Your Salary Ranges", value=", ".join(user_prefs.salary_ranges))
        await ctx.send(embed=embed)
    
    @commands.command(name="addwork")
    async def add_work_arrangement(self, ctx, arrangement: str = None):
        """Add a work arrangement preference. Usage: !addwork [arrangement] or !addwork for interactive selection"""
        if not arrangement:
            # Start interactive session
            await self.interactive_ui.start_addwork_session(ctx)
            return
        
        user_prefs = self.storage_service.get_user_preferences(ctx.author.id)
        user_prefs.add_work_arrangement(arrangement)
        self.storage_service.save_user_preferences(user_prefs)
        
        embed = discord.Embed(
            title="🏠 Work Arrangement Added!",
            description=f"Added **{arrangement}** to your work arrangement preferences",
            color=0x00ff00
        )
        embed.add_field(name="Your Work Arrangements", value=", ".join(user_prefs.work_arrangements))
        await ctx.send(embed=embed)
    
    # Priority preference commands
    @commands.command(name="addprioritycompany")
    async def add_priority_company(self, ctx, company: str):
        """Add a priority company for immediate alerts"""
        user_prefs = self.storage_service.get_user_preferences(ctx.author.id)
        user_prefs.add_priority_company(company)
        self.storage_service.save_user_preferences(user_prefs)
        
        embed = discord.Embed(
            title="🔥 Priority Company Added!",
            description=f"Added **{company}** to your priority companies",
            color=0xff6b35
        )
        embed.add_field(name="Your Priority Companies", value=", ".join(user_prefs.priority_companies))
        embed.add_field(name="Note", value="You'll get immediate alerts for jobs at priority companies!")
        await ctx.send(embed=embed)
    
    @commands.command(name="addprioritycategory")
    async def add_priority_category(self, ctx, category: str):
        """Add a priority category for immediate alerts"""
        user_prefs = self.storage_service.get_user_preferences(ctx.author.id)
        user_prefs.add_priority_category(category)
        self.storage_service.save_user_preferences(user_prefs)
        
        embed = discord.Embed(
            title="🔥 Priority Category Added!",
            description=f"Added **{category}** to your priority categories",
            color=0xff6b35
        )
        embed.add_field(name="Your Priority Categories", value=", ".join(user_prefs.priority_categories))
        embed.add_field(name="Note", value="You'll get immediate alerts for jobs in priority categories!")
        await ctx.send(embed=embed)
    
    @commands.command(name="setminsalary")
    async def set_min_salary(self, ctx, salary_min: int):
        """Set minimum salary requirement in thousands USD (e.g., !setminsalary 100 for $100k)"""
        user_prefs = self.storage_service.get_user_preferences(ctx.author.id)
        user_prefs.set_priority_salary_min(salary_min)
        self.storage_service.save_user_preferences(user_prefs)
        
        embed = discord.Embed(
            title="💰 Minimum Salary Set!",
            description=f"Set minimum salary requirement to **${salary_min}k**",
            color=0x00ff00
        )
        embed.add_field(name="Note", value="You'll get priority alerts for jobs at or above this salary!")
        await ctx.send(embed=embed)
    
    # Notification preference commands
    @commands.command(name="setnotifications")
    async def set_notification_frequency(self, ctx, frequency: str):
        """Set notification frequency. Options: immediate, hourly, daily, weekly, digest"""
        if frequency.lower() not in Config.NOTIFICATION_FREQUENCIES:
            embed = discord.Embed(
                title="❌ Invalid Frequency",
                description=f"Valid options: {', '.join(Config.NOTIFICATION_FREQUENCIES)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        user_prefs = self.storage_service.get_user_preferences(ctx.author.id)
        user_prefs.notification_frequency = frequency.lower()
        self.storage_service.save_user_preferences(user_prefs)
        
        embed = discord.Embed(
            title="🔔 Notification Frequency Updated!",
            description=f"Set to **{frequency}** notifications",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="setnotificationtime")
    async def set_notification_time(self, ctx, hour: int, minute: int = 0):
        """Set notification time for scheduled notifications (24-hour format)"""
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            embed = discord.Embed(
                title="❌ Invalid Time",
                description="Hour must be 0-23, minute must be 0-59",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        user_prefs = self.storage_service.get_user_preferences(ctx.author.id)
        user_prefs.set_notification_time(hour, minute)
        self.storage_service.save_user_preferences(user_prefs)
        
        embed = discord.Embed(
            title="⏰ Notification Time Set!",
            description=f"Set to **{hour:02d}:{minute:02d}** daily",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="clearpreferences")
    async def clear_preferences(self, ctx):
        """Clear all your job preferences"""
        user_prefs = self.storage_service.get_user_preferences(ctx.author.id)
        user_prefs.categories = []
        user_prefs.locations = []
        user_prefs.companies = []
        user_prefs.experience_levels = []
        user_prefs.salary_ranges = []
        user_prefs.work_arrangements = []
        user_prefs.priority_companies = []
        user_prefs.priority_categories = []
        user_prefs.priority_salary_min = None
        self.storage_service.save_user_preferences(user_prefs)
        
        embed = discord.Embed(
            title="🗑️ Preferences Cleared!",
            description="All your job preferences have been cleared",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="bothelp")
    async def help_command(self, ctx):
        """Show help information"""
        embed = discord.Embed(
            title="🤖 Job Hunt Bot Help",
            description="Here are the available commands:",
            color=0x0099ff
        )

        commands_info = [
            ("!checknow", "Manually check for new jobs"),
            ("!dumpjobs", "Interactive job search with filters"),
            ("!subscribe", "Interactive category subscription"),
            ("!unsubscribe", "Interactive category unsubscription"),
            ("!preferences", "Show your current preferences"),
            ("!addlocation", "Interactive location addition"),
            ("!addcompany", "Interactive company addition"),
            ("!addexperience", "Interactive experience level addition"),
            ("!addsalary", "Interactive salary range addition"),
            ("!addwork", "Interactive work arrangement addition"),
            ("!addprioritycompany", "Add priority company for alerts"),
            ("!addprioritycategory", "Add priority category for alerts"),
            ("!setminsalary", "Set minimum salary requirement"),
            ("!setnotifications", "Set notification frequency"),
            ("!setnotificationtime", "Set daily notification time"),
            ("!clearpreferences", "Clear all preferences"),
            ("!cancel", "Cancel your active interactive session"),
            ("!welcome", "Send yourself a welcome message"),
            ("!bothelp", "Show this help message")
        ]

        # Only show admin commands if in a guild and user has permissions
        if ctx.guild is not None:
            if hasattr(ctx.author, "guild_permissions") and ctx.author.guild_permissions.manage_messages:
                admin_commands = [
                    ("!postguide", "Post guide embed to configured guide channel")
                ]
                commands_info.extend(admin_commands)
        else:
            # DM context: add a note about limited functionality
            embed.add_field(
                name="⚠️ Note",
                value="Some admin commands are only available in servers.",
                inline=False
            )

        for cmd, desc in commands_info:
            embed.add_field(name=cmd, value=desc, inline=False)

        embed.add_field(
            name="💡 Tip", 
            value="Use `!subscribe` without a category to see available options!",
            inline=False
        )

        embed.add_field(
            name="🎯 Interactive Commands", 
            value="Most commands now support interactive UI! Just type `!dumpjobs`, `!subscribe`, etc. without arguments to use the emoji-based interface.",
            inline=False
        )

        embed.add_field(
            name="🔥 Priority Features", 
            value="Use priority commands to get immediate alerts for your dream companies and roles!",
            inline=False
        )

        embed.add_field(
            name="ℹ️ Note", 
            value="Use `!help` for Discord's built-in help, or `!bothelp` for bot-specific commands.",
            inline=False
        )

        await ctx.send(embed=embed)
    
    @commands.command(name="postguide")
    @commands.has_permissions(manage_messages=True)  # Only admins can post the guide
    async def post_guide_to_config(self, ctx):
        """Post the comprehensive guide embed to the configured guide channel"""
        if Config.GUIDE_CHANNEL_ID == 0:
            await ctx.send("❌ GUIDE_CHANNEL_ID not configured in .env file")
            return
        
        try:
            target_channel = self.bot.get_channel(Config.GUIDE_CHANNEL_ID)
            if not target_channel:
                await ctx.send(f"❌ Could not find configured guide channel: {Config.GUIDE_CHANNEL_ID}")
                return
            
            embed = discord.Embed(
                title="🤖 Job Hunt Buddy - Complete Guide",
                description="Welcome to Job Hunt Buddy! This bot automatically monitors job postings and sends personalized notifications.",
                color=0x0099ff,
                url="https://github.com/yourusername/jobhuntbuddy"  # Replace with your repo URL
            )

            # Privacy Tip
            embed.add_field(
                name="🔒 Privacy Tip",
                value="For privacy, DM the bot directly to set your job preferences and use personal commands (like `!subscribe`, `!preferences`, etc.).",
                inline=False
            )
            
            # Quick Start Section
            embed.add_field(
                name="🚀 Quick Start",
                value="```\n!subscribe software engineer\n!addlocation \"San Francisco\"\n!addprioritycompany discord\n!checknow\n```",
                inline=False
            )
            
            # Core Commands
            embed.add_field(
                name="🔍 Core Commands",
                value="• `!checknow` - Check for new jobs\n• `!dumpjobs` - Interactive job search\n• `!preferences` - View your settings",
                inline=True
            )
            
            # Preference Commands
            embed.add_field(
                name="⚙️ Preference Commands",
                value="• `!subscribe` - Interactive category subscription\n• `!addlocation` - Interactive location addition\n• `!addcompany` - Interactive company addition\n• `!addexperience` - Interactive experience level addition\n• `!addsalary` - Interactive salary range addition\n• `!addwork` - Interactive work arrangement addition",
                inline=True
            )
            
            # Priority Commands
            embed.add_field(
                name="🔥 Priority Commands",
                value="• `!addprioritycompany` - Add priority company\n• `!addprioritycategory` - Add priority category\n• `!setminsalary` - Set minimum salary\n• `!setnotifications` - Set notification frequency",
                inline=True
            )
            
            # Available Categories
            categories_text = "• " + "\n• ".join(Config.DEFAULT_CATEGORIES[:8])  # Show first 8
            embed.add_field(
                name="📋 Popular Categories",
                value=categories_text,
                inline=True
            )
            
            # Supported Companies
            embed.add_field(
                name="🏢 Supported Companies",
                value="• Discord\n• Reddit\n• Monarch Money\n• Cribl\n• Gitlab",
                inline=True
            )
            
            # How it works
            embed.add_field(
                name="🔄 How It Works",
                value="• Checks for new jobs every 2 hours\n• Filters based on your preferences\n• Sends personalized notifications\n• Priority alerts for dream companies/roles\n• No duplicates - each job posted once",
                inline=False
            )
            
            # Pro Tips
            embed.add_field(
                name="💡 Pro Tips",
                value="• Use `!subscribe` for interactive category selection\n• Use `!dumpjobs` for interactive job filtering\n• Add \"Remote\" as location for remote jobs\n• Set priority companies for immediate alerts\n• Use `!clearpreferences` to see all jobs\n• Check `!bothelp` for full command list",
                inline=False
            )
            
            embed.set_footer(text="Job Hunt Buddy v2.0 - Built with ❤️ for job seekers")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1234567890.png")  # Optional: Add bot avatar
            
            await target_channel.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error posting guide: {e}")
    
    @commands.command(name="welcome")
    async def send_welcome(self, ctx):
        """Send a welcome message to the user (can be used by admins or users)"""
        await self._send_welcome_message(ctx.author)
    
    async def _send_welcome_message(self, user):
        """Send a welcome message to a specific user"""
        embed = discord.Embed(
            title="🎉 Welcome to Job Hunt Buddy!",
            description=f"Hi {user.mention}! I'm here to help you find your next job opportunity.",
            color=0x00ff00
        )
        
        embed.add_field(
            name="🚀 Get Started",
            value="1. **Subscribe to job categories**: `!subscribe` (interactive)\n2. **Add location preferences**: `!addlocation` (interactive)\n3. **Set priority companies**: `!addprioritycompany discord`\n4. **Search for jobs**: `!dumpjobs` (interactive)",
            inline=False
        )
        
        embed.add_field(
            name="📋 Popular Commands",
            value="• `!subscribe` - Interactive category subscription\n• `!preferences` - View your current settings\n• `!bothelp` - Show all commands\n• `!dumpjobs` - Interactive job search",
            inline=False
        )
        
        embed.add_field(
            name="🔥 Priority Features",
            value="• `!addprioritycompany` - Get immediate alerts for dream companies\n• `!addprioritycategory` - Get immediate alerts for dream roles\n• `!setminsalary` - Set minimum salary requirements\n• `!setnotifications` - Customize notification frequency",
            inline=False
        )
        
        embed.add_field(
            name="💡 Quick Tips",
            value="• I check for new jobs every 2 hours automatically\n• You'll only see jobs that match your preferences\n• Priority jobs get immediate alerts\n• Use `!clearpreferences` to see all jobs\n• Each job is posted only once\n• **NEW**: Enhanced filtering with experience, salary, and work arrangements!",
            inline=False
        )
        
        embed.set_footer(text="Need help? Ask an admin or use !bothelp for more commands")
        
        try:
            await user.send(embed=embed)
            return True
        except discord.Forbidden:
            # User has DMs disabled, can't send welcome message
            return False
    
    @commands.command(name="cancel")
    async def cancel_session(self, ctx):
        """Cancel your active interactive session"""
        if ctx.author.id in self.interactive_ui.active_sessions:
            session = self.interactive_ui.active_sessions[ctx.author.id]
            await session.cancel_session()
            await ctx.send("✅ Your active session has been cancelled.")
        else:
            await ctx.send("ℹ️ You don't have any active sessions to cancel.") 