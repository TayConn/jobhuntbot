import discord
from discord.ext import commands
from typing import List
from ..services.job_monitor import JobMonitor
from ..services.storage_service import StorageService
from ..services.notification_service import NotificationService
from ..models.user_preferences import UserPreferences
from ..utils.config import Config

class JobBotCommands(commands.Cog):
    """Discord bot commands for job hunting"""
    
    def __init__(self, bot, job_monitor: JobMonitor, 
                 notification_service: NotificationService):
        self.bot = bot
        self.job_monitor = job_monitor
        self.notification_service = notification_service
        self.storage_service = StorageService()
    
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
        !dumpjobs                                    - Show all jobs
        !dumpjobs category="backend"                 - Filter by category
        !dumpjobs location="Remote"                  - Filter by location  
        !dumpjobs company="discord"                  - Filter by company
        !dumpjobs category="backend, frontend"       - Multiple categories
        !dumpjobs category="backend" location="Remote" - Multiple filters
        """
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
        
        Expected format: category="backend, frontend" location="Remote" company="discord"
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
            
            return filter_prefs if (filter_prefs.categories or filter_prefs.locations or filter_prefs.companies) else None
            
        except Exception as e:
            print(f"[ERROR] Failed to parse dump filters: {e}")
            return None
    
    @commands.command(name="subscribe")
    async def subscribe(self, ctx, category: str = None):
        """Subscribe to job categories. Usage: !subscribe [category] or !subscribe to see available categories"""
        if not category:
            # Show available categories
            embed = discord.Embed(
                title="📋 Available Job Categories",
                description="Use `!subscribe <category>` to subscribe to a category",
                color=0x0099ff
            )
            
            categories_text = "\n".join([f"• {cat}" for cat in Config.DEFAULT_CATEGORIES])
            embed.add_field(name="Categories", value=categories_text, inline=False)
            
            embed.add_field(
                name="Examples", 
                value="`!subscribe software engineer`\n`!subscribe frontend`\n`!subscribe product manager`",
                inline=False
            )
            
            await ctx.send(embed=embed)
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
        user_prefs = self.storage_service.get_user_preferences(ctx.author.id)
        
        if not category:
            # Show current subscriptions
            embed = discord.Embed(
                title="📋 Your Current Subscriptions",
                description="Use `!unsubscribe <category>` to unsubscribe",
                color=0x0099ff
            )
            
            if user_prefs.categories:
                categories_text = "\n".join([f"• {cat}" for cat in user_prefs.categories])
                embed.add_field(name="Categories", value=categories_text, inline=False)
            else:
                embed.add_field(name="Categories", value="No categories subscribed", inline=False)
            
            await ctx.send(embed=embed)
            return
        
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
            name="Notification Frequency", 
            value=user_prefs.notification_frequency,
            inline=False
        )
        embed.add_field(
            name="Status", 
            value="Active" if user_prefs.is_active else "Inactive",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="addlocation")
    async def add_location(self, ctx, location: str):
        """Add a location preference. Usage: !addlocation 'San Francisco'"""
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
    async def add_company(self, ctx, company: str):
        """Add a company preference. Usage: !addcompany discord"""
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
    
    @commands.command(name="clearpreferences")
    async def clear_preferences(self, ctx):
        """Clear all your job preferences"""
        user_prefs = self.storage_service.get_user_preferences(ctx.author.id)
        user_prefs.categories = []
        user_prefs.locations = []
        user_prefs.companies = []
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
            ("!dumpjobs [filters]", "Show all current job listings with optional filters"),
            ("!subscribe [category]", "Subscribe to job categories"),
            ("!unsubscribe [category]", "Unsubscribe from job categories"),
            ("!preferences", "Show your current preferences"),
            ("!addlocation [location]", "Add location preference"),
            ("!addcompany [company]", "Add company preference"),
            ("!clearpreferences", "Clear all preferences"),
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
            name="🔍 Dumpjobs Filtering", 
            value="Use `!dumpjobs category=\"backend\" location=\"Remote\"` to filter results. Large results are sent as files.",
            inline=False
        )

        embed.add_field(
            name="ℹ️ Note", 
            value="Use `!help` for Discord's built-in help, or `!bothelp` for bot-specific commands.",
            inline=False
        )

        await ctx.send(embed=embed)
        """Post the comprehensive guide embed to the channel"""
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
            value="```\n!subscribe software engineer\n!addlocation \"San Francisco\"\n!checknow\n```",
            inline=False
        )
        
        # Core Commands
        embed.add_field(
            name="🔍 Core Commands",
            value="• `!checknow` - Check for new jobs\n• `!dumpjobs [filters]` - Show all current jobs\n• `!preferences` - View your settings",
            inline=True
        )
        
        # Preference Commands
        embed.add_field(
            name="⚙️ Preference Commands",
            value="• `!subscribe [category]` - Subscribe to job types\n• `!addlocation [location]` - Add location filter\n• `!addcompany [company]` - Add company filter",
            inline=True
        )
        
        # Available Categories
        categories_text = "• " + "\n• ".join(Config.DEFAULT_CATEGORIES[:6])  # Show first 6
        embed.add_field(
            name="📋 Popular Categories",
            value=categories_text,
            inline=True
        )
        
        # Supported Companies
        embed.add_field(
            name="🏢 Supported Companies",
            value="• Discord\n• Reddit\n• Monarch Money",
            inline=True
        )
        
        # How it works
        embed.add_field(
            name="🔄 How It Works",
            value="• Checks for new jobs every 2 hours\n• Filters based on your preferences\n• Sends notifications to this channel\n• No duplicates - each job posted once",
            inline=False
        )
        
        # Pro Tips
        embed.add_field(
            name="💡 Pro Tips",
            value="• Use `!subscribe` to see all categories\n• Add \"Remote\" as location for remote jobs\n• Use `!clearpreferences` to see all jobs\n• Use `!dumpjobs category=\"backend\" location=\"Remote\"` to filter results\n• Check `!bothelp` for full command list",
            inline=False
        )

        
        embed.set_footer(text="Job Hunt Buddy v1.0 - Built with ❤️ for job seekers")
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1234567890.png")  # Optional: Add bot avatar
        
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
                value="```\n!subscribe software engineer\n!addlocation \"San Francisco\"\n!checknow\n```",
                inline=False
            )
            
            # Core Commands
            embed.add_field(
                name="🔍 Core Commands",
                value="• `!checknow` - Check for new jobs\n• `!dumpjobs [filters]` - Show all current jobs\n• `!preferences` - View your settings",
                inline=True
            )
            
            # Preference Commands
            embed.add_field(
                name="⚙️ Preference Commands",
                value="• `!subscribe [category]` - Subscribe to job types\n• `!addlocation [location]` - Add location filter\n• `!addcompany [company]` - Add company filter",
                inline=True
            )
            
            # Available Categories
            categories_text = "• " + "\n• ".join(Config.DEFAULT_CATEGORIES[:6])  # Show first 6
            embed.add_field(
                name="📋 Popular Categories",
                value=categories_text,
                inline=True
            )
            
            # Supported Companies
            embed.add_field(
                name="🏢 Supported Companies",
                value="• Discord\n• Reddit\n• Monarch Money",
                inline=True
            )
            
            # How it works
            embed.add_field(
                name="🔄 How It Works",
                value="• Checks for new jobs every 2 hours\n• Filters based on your preferences\n• Sends notifications to this channel\n• No duplicates - each job posted once",
                inline=False
            )
            
            # Pro Tips
            embed.add_field(
                name="💡 Pro Tips",
                value="• Use `!subscribe` to see all categories\n• Add \"Remote\" as location for remote jobs\n• Use `!clearpreferences` to see all jobs\n• Use `!dumpjobs category=\"backend\" location=\"Remote\"` to filter results\n• Check `!bothelp` for full command list",
                inline=False
            )
            
            embed.set_footer(text="Job Hunt Buddy v1.0 - Built with ❤️ for job seekers")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1234567890.png")  # Optional: Add bot avatar
            
            await target_channel.send(embed=embed)
            #await ctx.send(f"✅ Guide posted to configured channel: <#{Config.GUIDE_CHANNEL_ID}>")
            
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
            value="1. **Subscribe to job categories**: `!subscribe software engineer`\n2. **Add location preferences**: `!addlocation \"San Francisco\"`\n3. **Check for jobs**: `!checknow`",
            inline=False
        )
        
        embed.add_field(
            name="📋 Popular Commands",
            value="• `!subscribe` - See available job categories\n• `!preferences` - View your current settings\n• `!bothelp` - Show all commands\n• `!dumpjobs [filters]` - See all current openings",
            inline=False
        )
        
        embed.add_field(
            name="💡 Quick Tips",
            value="• I check for new jobs every 2 hours automatically\n• You'll only see jobs that match your preferences\n• Use `!clearpreferences` to see all jobs\n• Each job is posted only once",
            inline=False
        )
        
        embed.set_footer(text="Need help? Ask an admin or use !bothelp for more commands")
        
        try:
            await user.send(embed=embed)
            return True
        except discord.Forbidden:
            # User has DMs disabled, can't send welcome message
            return False 