import discord
from discord.ext import commands
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from ..models.user_preferences import UserPreferences
from ..services.storage_service import StorageService
from ..utils.config import Config

class InteractiveUI:
    """Interactive UI system for emoji-based command interactions"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage_service = StorageService()
        self.active_sessions: Dict[int, 'UISession'] = {}  # user_id -> session
        
    async def start_dumpjobs_session(self, ctx):
        """Start interactive dumpjobs filter selection"""
        session = DumpJobsSession(ctx, self)
        self.active_sessions[ctx.author.id] = session
        await session.start()
    
    async def start_subscribe_session(self, ctx):
        """Start interactive category subscription"""
        session = SubscribeSession(ctx, self)
        self.active_sessions[ctx.author.id] = session
        await session.start()
    
    async def start_unsubscribe_session(self, ctx):
        """Start interactive category unsubscription"""
        session = UnsubscribeSession(ctx, self)
        self.active_sessions[ctx.author.id] = session
        await session.start()
    
    async def start_addlocation_session(self, ctx):
        """Start interactive location addition"""
        session = AddLocationSession(ctx, self)
        self.active_sessions[ctx.author.id] = session
        await session.start()
    
    async def start_addcompany_session(self, ctx):
        """Start interactive company addition"""
        session = AddCompanySession(ctx, self)
        self.active_sessions[ctx.author.id] = session
        await session.start()
    
    async def handle_reaction(self, payload):
        """Handle reaction events for active sessions"""
        if payload.user_id == self.bot.user.id:
            return  # Ignore bot's own reactions
        
        user_id = payload.user_id
        if user_id not in self.active_sessions:
            return
        
        session = self.active_sessions[user_id]
        if session.message_id != payload.message_id:
            return
        
        # Check if session has expired (30 minutes)
        if datetime.now() - session.created_at > timedelta(minutes=30):
            del self.active_sessions[user_id]
            return
        
        await session.handle_reaction(payload)
    
    def cleanup_session(self, user_id: int):
        """Clean up a completed or expired session"""
        if user_id in self.active_sessions:
            del self.active_sessions[user_id]

class UISession:
    """Base class for interactive UI sessions"""
    
    def __init__(self, ctx, ui_system: InteractiveUI):
        self.ctx = ctx
        self.ui_system = ui_system
        self.message_id: Optional[int] = None
        self.created_at = datetime.now()
    
    async def start(self):
        """Start the interactive session - to be implemented by subclasses"""
        pass
    
    async def handle_reaction(self, payload):
        """Handle reaction events - to be implemented by subclasses"""
        pass

class DumpJobsSession(UISession):
    """Interactive session for dumpjobs filtering"""
    
    def __init__(self, ctx, ui_system: InteractiveUI):
        super().__init__(ctx, ui_system)
        self.selected_categories: Set[str] = set()
        self.selected_locations: Set[str] = set()
        self.selected_companies: Set[str] = set()
        self.current_step = "main"  # main, category, location, company
    
    async def start(self):
        """Start the dumpjobs interactive session"""
        embed = discord.Embed(
            title="🔍 Interactive Job Search",
            description="Select filters by reacting with the emojis below:",
            color=0x0099ff
        )
        
        embed.add_field(
            name="📋 Available Filters",
            value="🗂 **Categories** - Job types (backend, frontend, etc.)\n"
                  "🌍 **Locations** - Job locations (Remote, San Francisco, etc.)\n"
                  "🏢 **Companies** - Specific companies (Discord, Reddit, etc.)",
            inline=False
        )
        
        embed.add_field(
            name="🎯 How to Use",
            value="1. Click an emoji to select that filter type\n"
                  "2. Select your options from the list\n"
                  "3. Click 🟢 when done to run the search\n"
                  "4. Click ❌ to cancel",
            inline=False
        )
        
        embed.add_field(
            name="💡 Tip",
            value="You can select multiple options for each filter type. Leave filters empty to see all jobs.",
            inline=False
        )
        
        embed.set_footer(text="Session expires in 30 minutes")
        
        message = await self.ctx.send(embed=embed)
        self.message_id = message.id
        
        # Add reaction options
        await message.add_reaction("🗂")  # Categories
        await message.add_reaction("🌍")  # Locations
        await message.add_reaction("🏢")  # Companies
        await message.add_reaction("🟢")  # Done
        await message.add_reaction("❌")  # Cancel
    
    async def handle_reaction(self, payload):
        """Handle reaction events"""
        emoji = str(payload.emoji)
        
        if emoji == "❌":
            await self.cancel_session()
            return
        
        if emoji == "🟢":
            await self.run_search()
            return
        
        if emoji == "🗂":
            await self.show_category_options()
        elif emoji == "🌍":
            await self.show_location_options()
        elif emoji == "🏢":
            await self.show_company_options()
        elif emoji == "🔄":
            await self.show_main_menu()
        else:
            # Handle specific selections based on current step
            if self.current_step == "category":
                await self.handle_category_selection(emoji)
            elif self.current_step == "location":
                await self.handle_location_selection(emoji)
            elif self.current_step == "company":
                await self.handle_company_selection(emoji)
    
    async def show_main_menu(self):
        """Show the main menu"""
        embed = discord.Embed(
            title="🔍 Interactive Job Search",
            description="Select filters by reacting with the emojis below:",
            color=0x0099ff
        )
        
        embed.add_field(
            name="📋 Available Filters",
            value="🗂 **Categories** - Job types (backend, frontend, etc.)\n"
                  "🌍 **Locations** - Job locations (Remote, San Francisco, etc.)\n"
                  "🏢 **Companies** - Specific companies (Discord, Reddit, etc.)",
            inline=False
        )
        
        # Show current selections
        selections = []
        if self.selected_categories:
            selections.append(f"Categories: {', '.join(self.selected_categories)}")
        if self.selected_locations:
            selections.append(f"Locations: {', '.join(self.selected_locations)}")
        if self.selected_companies:
            selections.append(f"Companies: {', '.join(self.selected_companies)}")
        
        if selections:
            embed.add_field(name="Current Selections", value="\n".join(selections), inline=False)
        
        embed.add_field(
            name="Actions",
            value="🟢 **Done** - Run search with current filters\n"
                  "❌ **Cancel** - Cancel search",
            inline=False
        )
        
        embed.set_footer(text="Session expires in 30 minutes")
        
        channel = self.ctx.channel
        message = await channel.fetch_message(self.message_id)
        await message.edit(embed=embed)
        
        # Clear old reactions and add new ones
        await message.clear_reactions()
        await message.add_reaction("🗂")  # Categories
        await message.add_reaction("🌍")  # Locations
        await message.add_reaction("🏢")  # Companies
        await message.add_reaction("🟢")  # Done
        await message.add_reaction("❌")  # Cancel
        
        self.current_step = "main"
    
    async def show_category_options(self):
        """Show available categories for selection"""
        embed = discord.Embed(
            title="🗂 Select Job Categories",
            description="React to select categories. You can select multiple:",
            color=0x0099ff
        )
        
        # Show available categories with number emojis
        categories = Config.DEFAULT_CATEGORIES
        category_text = ""
        for i, category in enumerate(categories[:10]):  # Limit to 10 for emoji reactions
            emoji = f"{i+1}️⃣"
            check = "✅" if category in self.selected_categories else "⬜"
            category_text += f"{emoji} {check} {category}\n"
        
        embed.add_field(name="Categories", value=category_text, inline=False)
        embed.add_field(
            name="Selected", 
            value=", ".join(self.selected_categories) if self.selected_categories else "None",
            inline=False
        )
        embed.add_field(
            name="Actions",
            value="🔄 **Back** - Return to main menu\n"
                  "🟢 **Done** - Run search with current filters",
            inline=False
        )
        
        # Update the message
        channel = self.ctx.channel
        message = await channel.fetch_message(self.message_id)
        await message.edit(embed=embed)
        
        # Clear old reactions and add new ones
        await message.clear_reactions()
        for i in range(min(10, len(categories))):
            await message.add_reaction(f"{i+1}️⃣")
        await message.add_reaction("🔄")  # Back
        await message.add_reaction("🟢")  # Done
        await message.add_reaction("❌")  # Cancel
        
        self.current_step = "category"
    
    async def show_location_options(self):
        """Show available locations for selection"""
        embed = discord.Embed(
            title="🌍 Select Job Locations",
            description="React to select locations. You can select multiple:",
            color=0x0099ff
        )
        
        # Common locations
        locations = ["Remote", "San Francisco", "New York", "Los Angeles", "Seattle", "Austin", "Boston", "Chicago"]
        location_text = ""
        for i, location in enumerate(locations):
            emoji = f"{chr(65+i)}️⃣"  # A, B, C, etc.
            check = "✅" if location in self.selected_locations else "⬜"
            location_text += f"{emoji} {check} {location}\n"
        
        embed.add_field(name="Locations", value=location_text, inline=False)
        embed.add_field(
            name="Selected", 
            value=", ".join(self.selected_locations) if self.selected_locations else "None",
            inline=False
        )
        embed.add_field(
            name="Actions",
            value="🔄 **Back** - Return to main menu\n"
                  "🟢 **Done** - Run search with current filters",
            inline=False
        )
        
        # Update the message
        channel = self.ctx.channel
        message = await channel.fetch_message(self.message_id)
        await message.edit(embed=embed)
        
        # Clear old reactions and add new ones
        await message.clear_reactions()
        for i in range(len(locations)):
            await message.add_reaction(f"{chr(65+i)}️⃣")
        await message.add_reaction("🔄")  # Back
        await message.add_reaction("🟢")  # Done
        await message.add_reaction("❌")  # Cancel
        
        self.current_step = "location"
    
    async def show_company_options(self):
        """Show available companies for selection"""
        embed = discord.Embed(
            title="🏢 Select Companies",
            description="React to select companies. You can select multiple:",
            color=0x0099ff
        )
        
        companies = ["Discord", "Reddit", "Monarch Money"]
        company_text = ""
        for i, company in enumerate(companies):
            emoji = f"{chr(65+i)}️⃣"  # A, B, C
            check = "✅" if company in self.selected_companies else "⬜"
            company_text += f"{emoji} {check} {company}\n"
        
        embed.add_field(name="Companies", value=company_text, inline=False)
        embed.add_field(
            name="Selected", 
            value=", ".join(self.selected_companies) if self.selected_companies else "None",
            inline=False
        )
        embed.add_field(
            name="Actions",
            value="🔄 **Back** - Return to main menu\n"
                  "🟢 **Done** - Run search with current filters",
            inline=False
        )
        
        # Update the message
        channel = self.ctx.channel
        message = await channel.fetch_message(self.message_id)
        await message.edit(embed=embed)
        
        # Clear old reactions and add new ones
        await message.clear_reactions()
        for i in range(len(companies)):
            await message.add_reaction(f"{chr(65+i)}️⃣")
        await message.add_reaction("🔄")  # Back
        await message.add_reaction("🟢")  # Done
        await message.add_reaction("❌")  # Cancel
        
        self.current_step = "company"
    
    async def handle_category_selection(self, emoji):
        """Handle category selection"""
        # Map emoji to category index
        emoji_to_index = {f"{i+1}️⃣": i for i in range(10)}
        if emoji in emoji_to_index:
            index = emoji_to_index[emoji]
            if index < len(Config.DEFAULT_CATEGORIES):
                category = Config.DEFAULT_CATEGORIES[index]
                if category in self.selected_categories:
                    self.selected_categories.remove(category)
                else:
                    self.selected_categories.add(category)
                await self.show_category_options()
    
    async def handle_location_selection(self, emoji):
        """Handle location selection"""
        locations = ["Remote", "San Francisco", "New York", "Los Angeles", "Seattle", "Austin", "Boston", "Chicago"]
        emoji_to_index = {f"{chr(65+i)}️⃣": i for i in range(len(locations))}
        if emoji in emoji_to_index:
            index = emoji_to_index[emoji]
            location = locations[index]
            if location in self.selected_locations:
                self.selected_locations.remove(location)
            else:
                self.selected_locations.add(location)
            await self.show_location_options()
    
    async def handle_company_selection(self, emoji):
        """Handle company selection"""
        companies = ["Discord", "Reddit", "Monarch Money"]
        emoji_to_index = {f"{chr(65+i)}️⃣": i for i in range(len(companies))}
        if emoji in emoji_to_index:
            index = emoji_to_index[emoji]
            company = companies[index]
            if company in self.selected_companies:
                self.selected_companies.remove(company)
            else:
                self.selected_companies.add(company)
            await self.show_company_options()
    
    async def cancel_session(self):
        """Cancel the session"""
        embed = discord.Embed(
            title="❌ Session Cancelled",
            description="Job search session has been cancelled.",
            color=0xff0000
        )
        
        channel = self.ctx.channel
        message = await channel.fetch_message(self.message_id)
        await message.edit(embed=embed)
        await message.clear_reactions()
        
        self.ui_system.cleanup_session(self.ctx.author.id)
    
    async def run_search(self):
        """Run the job search with selected filters"""
        # Create filter preferences
        filter_prefs = UserPreferences(user_id=0)
        filter_prefs.categories = list(self.selected_categories)
        filter_prefs.locations = list(self.selected_locations)
        filter_prefs.companies = list(self.selected_companies)
        
        # Show summary
        embed = discord.Embed(
            title="🔍 Running Job Search",
            description="Searching for jobs with your selected filters...",
            color=0x00ff00
        )
        
        if filter_prefs.categories:
            embed.add_field(name="Categories", value=", ".join(filter_prefs.categories), inline=True)
        if filter_prefs.locations:
            embed.add_field(name="Locations", value=", ".join(filter_prefs.locations), inline=True)
        if filter_prefs.companies:
            embed.add_field(name="Companies", value=", ".join(filter_prefs.companies), inline=True)
        
        channel = self.ctx.channel
        message = await channel.fetch_message(self.message_id)
        await message.edit(embed=embed)
        await message.clear_reactions()
        
        # Run the actual job search
        try:
            from ..services.job_monitor import JobMonitor
            from ..services.notification_service import NotificationService
            
            notification_service = NotificationService(self.ui_system.bot, 0)  # channel_id doesn't matter for this
            job_monitor = JobMonitor(notification_service)
            
            jobs_by_company = await job_monitor.run_full_job_dump()
            
            # Apply filters
            if filter_prefs.categories or filter_prefs.locations or filter_prefs.companies:
                filtered_jobs_by_company = {}
                for company, jobs in jobs_by_company.items():
                    filtered_jobs = [
                        job for job in jobs 
                        if job.matches_user_preferences(filter_prefs)
                    ]
                    if filtered_jobs:
                        filtered_jobs_by_company[company] = filtered_jobs
                jobs_by_company = filtered_jobs_by_company
            
            # Send results
            await notification_service.send_job_dump(jobs_by_company, channel)
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred while searching for jobs: {e}",
                color=0xff0000
            )
            await message.edit(embed=error_embed)
        
        self.ui_system.cleanup_session(self.ctx.author.id)

class SubscribeSession(UISession):
    """Interactive session for subscribing to categories"""
    
    def __init__(self, ctx, ui_system: InteractiveUI):
        super().__init__(ctx, ui_system)
        self.selected_categories: Set[str] = set()
    
    async def start(self):
        """Start the subscribe interactive session"""
        embed = discord.Embed(
            title="📋 Subscribe to Job Categories",
            description="React to select categories you want to subscribe to:",
            color=0x0099ff
        )
        
        # Show available categories
        categories = Config.DEFAULT_CATEGORIES
        category_text = ""
        for i, category in enumerate(categories[:10]):  # Limit to 10 for emoji reactions
            emoji = f"{i+1}️⃣"
            category_text += f"{emoji} {category}\n"
        
        embed.add_field(name="Available Categories", value=category_text, inline=False)
        embed.add_field(
            name="Selected", 
            value=", ".join(self.selected_categories) if self.selected_categories else "None",
            inline=False
        )
        embed.add_field(
            name="Actions",
            value="🟢 **Subscribe** - Add selected categories\n"
                  "❌ **Cancel** - Cancel subscription",
            inline=False
        )
        
        message = await self.ctx.send(embed=embed)
        self.message_id = message.id
        
        # Add reaction options
        for i in range(min(10, len(categories))):
            await message.add_reaction(f"{i+1}️⃣")
        await message.add_reaction("🟢")  # Subscribe
        await message.add_reaction("❌")  # Cancel
    
    async def handle_reaction(self, payload):
        """Handle reaction events"""
        emoji = str(payload.emoji)
        
        if emoji == "❌":
            await self.cancel_session()
            return
        
        if emoji == "🟢":
            await self.subscribe_categories()
            return
        
        # Handle category selection
        emoji_to_index = {f"{i+1}️⃣": i for i in range(10)}
        if emoji in emoji_to_index:
            index = emoji_to_index[emoji]
            if index < len(Config.DEFAULT_CATEGORIES):
                category = Config.DEFAULT_CATEGORIES[index]
                if category in self.selected_categories:
                    self.selected_categories.remove(category)
                else:
                    self.selected_categories.add(category)
                await self.update_display()
    
    async def update_display(self):
        """Update the display with current selections"""
        embed = discord.Embed(
            title="📋 Subscribe to Job Categories",
            description="React to select categories you want to subscribe to:",
            color=0x0099ff
        )
        
        categories = Config.DEFAULT_CATEGORIES
        category_text = ""
        for i, category in enumerate(categories[:10]):
            emoji = f"{i+1}️⃣"
            check = "✅" if category in self.selected_categories else "⬜"
            category_text += f"{emoji} {check} {category}\n"
        
        embed.add_field(name="Available Categories", value=category_text, inline=False)
        embed.add_field(
            name="Selected", 
            value=", ".join(self.selected_categories) if self.selected_categories else "None",
            inline=False
        )
        embed.add_field(
            name="Actions",
            value="🟢 **Subscribe** - Add selected categories\n"
                  "❌ **Cancel** - Cancel subscription",
            inline=False
        )
        
        channel = self.ctx.channel
        message = await channel.fetch_message(self.message_id)
        await message.edit(embed=embed)
    
    async def cancel_session(self):
        """Cancel the session"""
        embed = discord.Embed(
            title="❌ Subscription Cancelled",
            description="Category subscription has been cancelled.",
            color=0xff0000
        )
        
        channel = self.ctx.channel
        message = await channel.fetch_message(self.message_id)
        await message.edit(embed=embed)
        await message.clear_reactions()
        
        self.ui_system.cleanup_session(self.ctx.author.id)
    
    async def subscribe_categories(self):
        """Subscribe to selected categories"""
        if not self.selected_categories:
            embed = discord.Embed(
                title="⚠️ No Categories Selected",
                description="Please select at least one category to subscribe to.",
                color=0xffff00
            )
            channel = self.ctx.channel
            message = await channel.fetch_message(self.message_id)
            await message.edit(embed=embed)
            return
        
        # Add categories to user preferences
        user_prefs = self.ui_system.storage_service.get_user_preferences(self.ctx.author.id)
        for category in self.selected_categories:
            user_prefs.add_category(category)
        self.ui_system.storage_service.save_user_preferences(user_prefs)
        
        embed = discord.Embed(
            title="✅ Subscribed!",
            description=f"You're now subscribed to {len(self.selected_categories)} categories:",
            color=0x00ff00
        )
        embed.add_field(name="Categories", value=", ".join(self.selected_categories), inline=False)
        embed.add_field(name="Your Total Categories", value=", ".join(user_prefs.categories) or "None", inline=False)
        
        channel = self.ctx.channel
        message = await channel.fetch_message(self.message_id)
        await message.edit(embed=embed)
        await message.clear_reactions()
        
        self.ui_system.cleanup_session(self.ctx.author.id)

# Additional session classes for other commands would follow the same pattern
class UnsubscribeSession(UISession):
    """Interactive session for unsubscribing from categories"""
    # Implementation similar to SubscribeSession but for unsubscribing
    
class AddLocationSession(UISession):
    """Interactive session for adding locations"""
    # Implementation for location selection
    
class AddCompanySession(UISession):
    """Interactive session for adding companies"""
    # Implementation for company selection 