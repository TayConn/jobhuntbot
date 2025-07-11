import discord
from discord.ext import commands
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from ..models.user_preferences import UserPreferences
from ..services.storage_service import StorageService
from ..utils.config import Config

# --- EMOJI CONSTANTS ---
NEXT_EMOJI = "✅"  # U+2705
PENCIL_EMOJI = "📝"  # U+1F4DD
CANCEL_EMOJI = "❌"  # U+274C

class InteractiveUI:
    """Interactive UI system for emoji-based command interactions"""
    
    def __init__(self, bot):
        self.bot = bot
        self.storage_service = StorageService()
        self.active_sessions: Dict[int, 'UISession'] = {}  # user_id -> session
        self.waiting_for_custom_location: Dict[int, 'DumpJobsSession'] = {}  # user_id -> session
        
    async def start_dumpjobs_session(self, ctx):
        """Start interactive dumpjobs filter selection"""
        # Check if user already has an active session
        if ctx.author.id in self.active_sessions:
            existing_session = self.active_sessions[ctx.author.id]
            await ctx.send("⚠️ You already have an active session. Please complete or cancel it first.")
            return
        
        session = DumpJobsSession(ctx, self)
        self.active_sessions[ctx.author.id] = session
        await session.start()
    
    async def start_subscribe_session(self, ctx):
        """Start interactive category subscription"""
        # Check if user already has an active session
        if ctx.author.id in self.active_sessions:
            existing_session = self.active_sessions[ctx.author.id]
            await ctx.send("⚠️ You already have an active session. Please complete or cancel it first.")
            return
        
        session = SubscribeSession(ctx, self)
        self.active_sessions[ctx.author.id] = session
        await session.start()
    
    async def start_unsubscribe_session(self, ctx):
        """Start interactive category unsubscription"""
        # Check if user already has an active session
        if ctx.author.id in self.active_sessions:
            existing_session = self.active_sessions[ctx.author.id]
            await ctx.send("⚠️ You already have an active session. Please complete or cancel it first.")
            return
        
        session = UnsubscribeSession(ctx, self)
        self.active_sessions[ctx.author.id] = session
        await session.start()
    
    async def start_addlocation_session(self, ctx):
        """Start interactive location addition"""
        # Check if user already has an active session
        if ctx.author.id in self.active_sessions:
            existing_session = self.active_sessions[ctx.author.id]
            await ctx.send("⚠️ You already have an active session. Please complete or cancel it first.")
            return
        
        session = AddLocationSession(ctx, self)
        self.active_sessions[ctx.author.id] = session
        await session.start()
    
    async def start_addcompany_session(self, ctx):
        """Start interactive company addition"""
        # Check if user already has an active session
        if ctx.author.id in self.active_sessions:
            existing_session = self.active_sessions[ctx.author.id]
            await ctx.send("⚠️ You already have an active session. Please complete or cancel it first.")
            return
        
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
        
        # Check if session has expired (30 minutes)
        if datetime.now() - session.created_at > timedelta(minutes=30):
            del self.active_sessions[user_id]
            return
        await session.handle_reaction(payload)
    
    async def handle_message(self, message):
        user_id = message.author.id
        if user_id in self.waiting_for_custom_location:
            session = self.waiting_for_custom_location.pop(user_id)
            await session.handle_custom_location_input(message.content)
    
    def cleanup_session(self, user_id: int):
        """Clean up a completed or expired session"""
        if user_id in self.active_sessions:
            del self.active_sessions[user_id]

    async def handle_reaction_remove(self, payload):
        if payload.user_id == self.bot.user.id:
            return  # Ignore bot's own reactions
        user_id = payload.user_id
        if user_id not in self.active_sessions:
            return
        session = self.active_sessions[user_id]
        await session.handle_reaction_remove(payload)

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

    async def handle_reaction_remove(self, payload):
        """Handle reaction removal events - to be implemented by subclasses"""
        pass

class DumpJobsSession(UISession):
    """Interactive session for dumpjobs filtering"""
    
    def __init__(self, ctx, ui_system: InteractiveUI):
        super().__init__(ctx, ui_system)
        self.selected_categories: Set[str] = set()
        self.selected_locations: Set[str] = set()
        self.custom_locations: Set[str] = set()
        self.selected_companies: Set[str] = set()
        self.step = 0  # 0=category, 1=location, 2=company, 3=summary
        self.messages: List[discord.Message] = []
        self.user_id = ctx.author.id
    
    async def start(self):
        """Start the dumpjobs interactive session"""
        await self.send_category_message()
    
    async def send_category_message(self):
        embed = discord.Embed(
            title="📋 Step 1 of 3: Select Job Categories",
            description="React to select categories. You can select multiple.",
            color=0x0099ff
        )
        categories = Config.DEFAULT_CATEGORIES[:10]
        for i, category in enumerate(categories):
            if i < 9:
                emoji = f"{i+1}️⃣"
            else:
                emoji = "🔟"
            embed.add_field(name=emoji, value=category, inline=False)
        embed.set_footer(text="When done, click ✅. ❌ to exit prompt.")
        msg = await self.ctx.send(embed=embed)
        self.messages.append(msg)
        for i in range(len(categories)):
            if i < 9:
                emoji = f"{i+1}️⃣"
            else:
                emoji = "🔟"
            await msg.add_reaction(emoji)
        await msg.add_reaction(NEXT_EMOJI)
        await msg.add_reaction(CANCEL_EMOJI)
        self.step = 0
        self.category_msg = msg
    
    async def send_location_message(self):
        embed = discord.Embed(
            title="🌍 Step 2: Select Job Locations",
            description="React to select locations. You can select multiple.\n"
                        "To add a custom location, click 📝 and type it in the chat (comma-separated for multiple).\n"
                        "Example: `Berlin, Paris, Tokyo`\n",
            color=0x0099ff
        )
        locations = ["Remote", "San Francisco", "New York", "Los Angeles", "Seattle", "Austin", "Boston", "Chicago"]
        for i, location in enumerate(locations):
            regional_emoji = chr(0x1F1E6 + i)  # 🇦, 🇧, ...
            embed.add_field(name=regional_emoji, value=location, inline=False)
        embed.add_field(name="📝", value="Custom Location", inline=False)
        embed.set_footer(text="When done, click ✅. ❌ to exit prompt.")
        msg = await self.ctx.send(embed=embed)
        self.messages.append(msg)
        for i in range(len(locations)):
            regional_emoji = chr(0x1F1E6 + i)
            await msg.add_reaction(regional_emoji)
        await msg.add_reaction(PENCIL_EMOJI)
        await msg.add_reaction(NEXT_EMOJI)
        await msg.add_reaction(CANCEL_EMOJI)
        self.step = 1
        self.location_msg = msg
    
    async def send_company_message(self):
        embed = discord.Embed(
            title="🏢 Step 3: Select Companies",
            description="React to select companies. You can select multiple.",
            color=0x0099ff
        )
        companies = ["Discord", "Reddit", "Monarch Money", "Cribl, Gitlab"]
        for i, company in enumerate(companies):
            regional_emoji = chr(0x1F1E6 + i)  # 🇦, 🇧, ...
            embed.add_field(name=regional_emoji, value=company, inline=False)
        embed.set_footer(text="When done, click ✅. ❌ to exit prompt.")
        msg = await self.ctx.send(embed=embed)
        self.messages.append(msg)
        for i in range(len(companies)):
            regional_emoji = chr(0x1F1E6 + i)
            await msg.add_reaction(regional_emoji)
        await msg.add_reaction(NEXT_EMOJI)
        await msg.add_reaction(CANCEL_EMOJI)
        self.step = 2
        self.company_msg = msg
    
    async def send_summary_message(self):
        embed = discord.Embed(
            title="✅ Summary: Your Job Search Filters",
            color=0x00ff00
        )
        if self.selected_categories:
            embed.add_field(name="Categories", value=", ".join(self.selected_categories), inline=False)
        if self.selected_locations or self.custom_locations:
            all_locs = list(self.selected_locations) + list(self.custom_locations)
            embed.add_field(name="Locations", value=", ".join(all_locs), inline=False)
        if self.selected_companies:
            embed.add_field(name="Companies", value=", ".join(self.selected_companies), inline=False)
        embed.set_footer(text="Click 🔍 to run search, 🔄 to start over, ❌ to cancel.")
        msg = await self.ctx.send(embed=embed)
        self.messages.append(msg)
        await msg.add_reaction("🔍")
        await msg.add_reaction("🔄")
        await msg.add_reaction(CANCEL_EMOJI)
        self.step = 3
        self.summary_msg = msg
    
    async def handle_reaction(self, payload):
        """Handle reaction events"""
        emoji = str(payload.emoji)
        
        if emoji == CANCEL_EMOJI:
            await self.cancel_session()
            return
        
        # Handle arrow right reactions more carefully - only process on current step's message
        if emoji == NEXT_EMOJI:
            if self.step == 0 and payload.message_id == self.category_msg.id:
                await self.send_location_message()
            elif self.step == 1 and payload.message_id == self.location_msg.id:
                await self.send_company_message()
            elif self.step == 2 and payload.message_id == self.company_msg.id:
                await self.send_summary_message()
            elif self.step == 3 and payload.message_id == self.summary_msg.id:
                await self.handle_summary_reaction(emoji)
            return
        
        # Handle other reactions based on current step and message
        if self.step == 0 and payload.message_id == self.category_msg.id:
            await self.handle_category_reaction(emoji)
        elif self.step == 1 and payload.message_id == self.location_msg.id:
            await self.handle_location_reaction(emoji)
        elif self.step == 2 and payload.message_id == self.company_msg.id:
            await self.handle_company_reaction(emoji)
        elif self.step == 3 and payload.message_id == self.summary_msg.id:
            await self.handle_summary_reaction(emoji)
    
    async def handle_category_reaction(self, emoji):
        """Handle category selection"""
        categories = Config.DEFAULT_CATEGORIES[:10]
        emoji_to_index = {f"{i+1}️⃣": i for i in range(10)}
        if emoji in emoji_to_index:
            idx = emoji_to_index[emoji]
            cat = categories[idx]
            if cat in self.selected_categories:
                self.selected_categories.remove(cat)
            else:
                self.selected_categories.add(cat)
    
    async def handle_location_reaction(self, emoji):
        """Handle location selection"""
        locations = ["Remote", "San Francisco", "New York", "Los Angeles", "Seattle", "Austin", "Boston", "Chicago"]
        emoji_to_index = {chr(0x1F1E6 + i): i for i in range(len(locations))}
        if emoji in emoji_to_index:
            idx = emoji_to_index[emoji]
            loc = locations[idx]
            if loc in self.selected_locations:
                self.selected_locations.remove(loc)
            else:
                self.selected_locations.add(loc)
        elif emoji == PENCIL_EMOJI:
            await self.prompt_custom_location()
    
    async def handle_company_reaction(self, emoji):
        """Handle company selection"""
        companies = ["Discord", "Reddit", "Monarch Money", "Cribl, Gitlab"]
        emoji_to_index = {chr(0x1F1E6 + i): i for i in range(len(companies))}
        if emoji in emoji_to_index:
            idx = emoji_to_index[emoji]
            comp = companies[idx]
            if comp in self.selected_companies:
                self.selected_companies.remove(comp)
            else:
                self.selected_companies.add(comp)
    
    async def prompt_custom_location(self):
        """Prompt for custom location input"""
        prompt = await self.ctx.send(
            "📝 Please type your custom location(s) in the chat. Separate multiple locations with commas.\nExample: `Berlin, Paris, Tokyo`"
        )
        self.ui_system.waiting_for_custom_location[self.user_id] = self
        self.messages.append(prompt)
    
    async def handle_custom_location_input(self, text):
        """Handle custom location input"""
        # Parse comma-separated locations
        locs = [loc.strip() for loc in text.split(",") if loc.strip()]
        self.custom_locations.update(locs)
        await self.ctx.send(f"✅ Added custom location(s): {', '.join(locs)}")
    
    async def handle_summary_reaction(self, emoji):
        """Handle summary reaction"""
        if emoji == "🔍":
            await self.run_search()
        elif emoji == "🔄":
            await self.restart()
        elif emoji == CANCEL_EMOJI:
            await self.cancel_session()
    
    async def run_search(self):
        """Run the job search with selected filters"""
        # Clean up session messages to reduce clutter
        for msg in self.messages:
            try:
                await msg.delete()
            except:
                pass  # Ignore errors if messages are already deleted
        
        # Create filter preferences
        filter_prefs = UserPreferences(user_id=0)
        filter_prefs.categories = list(self.selected_categories)
        filter_prefs.locations = list(self.selected_locations) + list(self.custom_locations)
        filter_prefs.companies = list(self.selected_companies)
        
        # Show summary
        await self.ctx.send("🔍 Running job search with your selected filters...")
        
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
            await notification_service.send_job_dump(jobs_by_company, self.ctx.channel)
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred while searching for jobs: {e}",
                color=0xff0000
            )
            await self.ctx.send(embed=error_embed)
        
        self.ui_system.cleanup_session(self.user_id)
    
    async def restart(self):
        """Restart the job search flow"""
        # Clean up old messages to reduce clutter
        for msg in self.messages:
            try:
                await msg.delete()
            except:
                pass  # Ignore errors if messages are already deleted
        
        # Clear selections and messages list
        self.selected_categories.clear()
        self.selected_locations.clear()
        self.custom_locations.clear()
        self.selected_companies.clear()
        self.messages.clear()
        
        await self.ctx.send("🔄 Restarting job search flow...")
        await self.send_category_message()
    
    async def cancel_session(self):
        """Cancel the session"""
        # Clean up messages to reduce clutter
        for msg in self.messages:
            try:
                await msg.delete()
            except:
                pass  # Ignore errors if messages are already deleted
        
        await self.ctx.send("❌ Job search session cancelled.")
        self.ui_system.cleanup_session(self.user_id)

    async def handle_reaction_remove(self, payload):
        emoji = str(payload.emoji)
        if self.step == 0 and payload.message_id == self.category_msg.id:
            await self.handle_category_remove(emoji)
        elif self.step == 1 and payload.message_id == self.location_msg.id:
            await self.handle_location_remove(emoji)
        elif self.step == 2 and payload.message_id == self.company_msg.id:
            await self.handle_company_remove(emoji)

    async def handle_category_remove(self, emoji):
        categories = Config.DEFAULT_CATEGORIES[:10]
        emoji_to_index = {f"{i+1}️⃣": i for i in range(10)}
        if emoji in emoji_to_index:
            idx = emoji_to_index[emoji]
            cat = categories[idx]
            self.selected_categories.discard(cat)

    async def handle_location_remove(self, emoji):
        locations = ["Remote", "San Francisco", "New York", "Los Angeles", "Seattle", "Austin", "Boston", "Chicago"]
        emoji_to_index = {chr(0x1F1E6 + i): i for i in range(len(locations))}
        if emoji in emoji_to_index:
            idx = emoji_to_index[emoji]
            loc = locations[idx]
            self.selected_locations.discard(loc)

    async def handle_company_remove(self, emoji):
        companies = ["Discord", "Reddit", "Monarch Money", "Cribl, Gitlab"]
        emoji_to_index = {chr(0x1F1E6 + i): i for i in range(len(companies))}
        if emoji in emoji_to_index:
            idx = emoji_to_index[emoji]
            comp = companies[idx]
            self.selected_companies.discard(comp)

class SubscribeSession(UISession):
    """Interactive session for subscribing to categories"""
    
    def __init__(self, ctx, ui_system: InteractiveUI):
        super().__init__(ctx, ui_system)
        self.selected_categories: Set[str] = set()
        self.step = 0
        self.messages: List[discord.Message] = []
        self.user_id = ctx.author.id

    async def start(self):
        await self.send_category_message()

    async def send_category_message(self):
        embed = discord.Embed(
            title="📋 Subscribe: Select Job Categories",
            description="React to select categories to subscribe. You can select multiple.",
            color=0x0099ff
        )
        categories = Config.DEFAULT_CATEGORIES[:10]
        for i, category in enumerate(categories):
            if i < 9:
                emoji = f"{i+1}️⃣"
            else:
                emoji = "🔟"
            embed.add_field(name=emoji, value=category, inline=False)
        embed.set_footer(text="When done, click ✅. ❌ to exit prompt.")
        msg = await self.ctx.send(embed=embed)
        self.messages.append(msg)
        for i in range(len(categories)):
            if i < 9:
                emoji = f"{i+1}️⃣"
            else:
                emoji = "🔟"
            await msg.add_reaction(emoji)
        await msg.add_reaction(NEXT_EMOJI)
        await msg.add_reaction(CANCEL_EMOJI)
        self.category_msg = msg

    async def handle_reaction(self, payload):
        emoji = str(payload.emoji)
        if payload.message_id == self.category_msg.id:
            await self.handle_category_reaction(emoji)

    async def handle_category_reaction(self, emoji):
        categories = Config.DEFAULT_CATEGORIES[:10]
        emoji_to_index = {f"{i+1}️⃣": i for i in range(10)}
        if emoji in emoji_to_index:
            idx = emoji_to_index[emoji]
            cat = categories[idx]
            if cat in self.selected_categories:
                self.selected_categories.remove(cat)
            else:
                self.selected_categories.add(cat)
        elif emoji == NEXT_EMOJI:
            await self.subscribe_categories()
        elif emoji == CANCEL_EMOJI:
            await self.cancel_session()

    async def subscribe_categories(self):
        if not self.selected_categories:
            await self.ctx.send("⚠️ Please select at least one category to subscribe.")
            return
        user_prefs = self.ui_system.storage_service.get_user_preferences(self.ctx.author.id)
        for category in self.selected_categories:
            user_prefs.add_category(category)
        self.ui_system.storage_service.save_user_preferences(user_prefs)
        embed = discord.Embed(
            title="✅ Subscribed!",
            description=f"You're now subscribed to: {', '.join(self.selected_categories)}",
            color=0x00ff00
        )
        await self.ctx.send(embed=embed)
        self.ui_system.cleanup_session(self.user_id)

    async def cancel_session(self):
        await self.ctx.send("❌ Subscription session cancelled.")
        self.ui_system.cleanup_session(self.user_id)

class UnsubscribeSession(UISession):
    """Interactive session for unsubscribing from categories"""
    def __init__(self, ctx, ui_system: InteractiveUI):
        super().__init__(ctx, ui_system)
        self.selected_categories: Set[str] = set()
        self.step = 0
        self.messages: List[discord.Message] = []
        self.user_id = ctx.author.id

    async def start(self):
        await self.send_category_message()

    async def send_category_message(self):
        user_prefs = self.ui_system.storage_service.get_user_preferences(self.ctx.author.id)
        categories = user_prefs.categories[:10]
        embed = discord.Embed(
            title="📋 Unsubscribe: Select Categories",
            description="React to select categories to unsubscribe. You can select multiple.",
            color=0x0099ff
        )
        for i, category in enumerate(categories):
            if i < 9:
                emoji = f"{i+1}️⃣"
            else:
                emoji = "🔟"
            embed.add_field(name=emoji, value=category, inline=False)
        embed.set_footer(text="When done, click ✅. ❌ to exit prompt.")
        msg = await self.ctx.send(embed=embed)
        self.messages.append(msg)
        for i in range(len(categories)):
            if i < 9:
                emoji = f"{i+1}️⃣"
            else:
                emoji = "🔟"
            await msg.add_reaction(emoji)
        await msg.add_reaction(NEXT_EMOJI)
        await msg.add_reaction(CANCEL_EMOJI)
        self.category_msg = msg
        self.categories = categories

    async def handle_reaction(self, payload):
        emoji = str(payload.emoji)
        if payload.message_id == self.category_msg.id:
            await self.handle_category_reaction(emoji)

    async def handle_category_reaction(self, emoji):
        emoji_to_index = {f"{i+1}️⃣": i for i in range(len(self.categories))}
        if emoji in emoji_to_index:
            idx = emoji_to_index[emoji]
            cat = self.categories[idx]
            if cat in self.selected_categories:
                self.selected_categories.remove(cat)
            else:
                self.selected_categories.add(cat)
        elif emoji == NEXT_EMOJI:
            await self.unsubscribe_categories()
        elif emoji == CANCEL_EMOJI:
            await self.cancel_session()

    async def unsubscribe_categories(self):
        if not self.selected_categories:
            await self.ctx.send("⚠️ Please select at least one category to unsubscribe.")
            return
        user_prefs = self.ui_system.storage_service.get_user_preferences(self.ctx.author.id)
        for category in self.selected_categories:
            user_prefs.remove_category(category)
        self.ui_system.storage_service.save_user_preferences(user_prefs)
        embed = discord.Embed(
            title="✅ Unsubscribed!",
            description=f"You have unsubscribed from: {', '.join(self.selected_categories)}",
            color=0x00ff00
        )
        await self.ctx.send(embed=embed)
        self.ui_system.cleanup_session(self.user_id)

    async def cancel_session(self):
        await self.ctx.send("❌ Unsubscribe session cancelled.")
        self.ui_system.cleanup_session(self.user_id)

class AddLocationSession(UISession):
    """Interactive session for adding locations"""
    def __init__(self, ctx, ui_system: InteractiveUI):
        super().__init__(ctx, ui_system)
        self.selected_locations: Set[str] = set()
        self.custom_locations: Set[str] = set()
        self.step = 0
        self.messages: List[discord.Message] = []
        self.user_id = ctx.author.id

    async def start(self):
        await self.send_location_message()

    async def send_location_message(self):
        embed = discord.Embed(
            title="🌍 Add Location: Select Locations",
            description="React to select locations to add. You can select multiple.\n"
                        "To add a custom location, click 📝 and type it in the chat (comma-separated for multiple).\n"
                        "Example: `Berlin, Paris, Tokyo`\n",
            color=0x0099ff
        )
        locations = ["Remote", "San Francisco", "New York", "Los Angeles", "Seattle", "Austin", "Boston", "Chicago"]
        for i, location in enumerate(locations):
            regional_emoji = chr(0x1F1E6 + i)  # 🇦, 🇧, ...
            embed.add_field(name=regional_emoji, value=location, inline=False)
        embed.add_field(name="📝", value="Custom Location", inline=False)
        embed.set_footer(text="When done, click ✅. ❌ to exit prompt.")
        msg = await self.ctx.send(embed=embed)
        self.messages.append(msg)
        for i in range(len(locations)):
            regional_emoji = chr(0x1F1E6 + i)
            await msg.add_reaction(regional_emoji)
        await msg.add_reaction(PENCIL_EMOJI)
        await msg.add_reaction(NEXT_EMOJI)
        await msg.add_reaction(CANCEL_EMOJI)
        self.location_msg = msg

    async def handle_reaction(self, payload):
        emoji = str(payload.emoji)
        if payload.message_id == self.location_msg.id:
            await self.handle_location_reaction(emoji)

    async def handle_location_reaction(self, emoji):
        locations = ["Remote", "San Francisco", "New York", "Los Angeles", "Seattle", "Austin", "Boston", "Chicago"]
        emoji_to_index = {chr(0x1F1E6 + i): i for i in range(len(locations))}
        if emoji in emoji_to_index:
            idx = emoji_to_index[emoji]
            loc = locations[idx]
            if loc in self.selected_locations:
                self.selected_locations.remove(loc)
            else:
                self.selected_locations.add(loc)
        elif emoji == PENCIL_EMOJI:
            await self.prompt_custom_location()
        elif emoji == NEXT_EMOJI:
            await self.add_locations()
        elif emoji == CANCEL_EMOJI:
            await self.cancel_session()

    async def prompt_custom_location(self):
        prompt = await self.ctx.send(
            "📝 Please type your custom location(s) in the chat. Separate multiple locations with commas.\nExample: `Berlin, Paris, Tokyo`"
        )
        self.ui_system.waiting_for_custom_location[self.user_id] = self
        self.messages.append(prompt)

    async def handle_custom_location_input(self, text):
        locs = [loc.strip() for loc in text.split(",") if loc.strip()]
        self.custom_locations.update(locs)
        await self.ctx.send(f"✅ Added custom location(s): {', '.join(locs)}")

    async def add_locations(self):
        if not self.selected_locations and not self.custom_locations:
            await self.ctx.send("⚠️ Please select or enter at least one location to add.")
            return
        user_prefs = self.ui_system.storage_service.get_user_preferences(self.ctx.author.id)
        for loc in self.selected_locations:
            user_prefs.add_location(loc)
        for loc in self.custom_locations:
            user_prefs.add_location(loc)
        self.ui_system.storage_service.save_user_preferences(user_prefs)
        embed = discord.Embed(
            title="✅ Location(s) Added!",
            description=f"Added: {', '.join(list(self.selected_locations) + list(self.custom_locations))}",
            color=0x00ff00
        )
        await self.ctx.send(embed=embed)
        await self.ui_system.start_addcompany_session(self.ctx)
        self.ui_system.cleanup_session(self.user_id)

    async def cancel_session(self):
        await self.ctx.send("❌ Add location session cancelled.")
        self.ui_system.cleanup_session(self.user_id)

class AddCompanySession(UISession):
    """Interactive session for adding companies"""
    def __init__(self, ctx, ui_system: InteractiveUI):
        super().__init__(ctx, ui_system)
        self.selected_companies: Set[str] = set()
        self.step = 0
        self.messages: List[discord.Message] = []
        self.user_id = ctx.author.id

    async def start(self):
        await self.send_company_message()

    async def send_company_message(self):
        embed = discord.Embed(
            title="🏢 Add Company: Select Companies",
            description="React to select companies to add. You can select multiple.",
            color=0x0099ff
        )
        companies = ["Discord", "Reddit", "Monarch Money", "Cribl, Gitlab"]
        for i, company in enumerate(companies):
            regional_emoji = chr(0x1F1E6 + i)  # 🇦, 🇧, ...
            embed.add_field(name=regional_emoji, value=company, inline=False)
        embed.set_footer(text="When done, click ✅. ❌ to exit prompt.")
        msg = await self.ctx.send(embed=embed)
        self.messages.append(msg)
        for i in range(len(companies)):
            regional_emoji = chr(0x1F1E6 + i)
            await msg.add_reaction(regional_emoji)
        await msg.add_reaction(NEXT_EMOJI)
        await msg.add_reaction(CANCEL_EMOJI)
        self.company_msg = msg

    async def handle_reaction(self, payload):
        emoji = str(payload.emoji)
        if payload.message_id == self.company_msg.id:
            await self.handle_company_reaction(emoji)

    async def handle_company_reaction(self, emoji):
        companies = ["Discord", "Reddit", "Monarch Money", "Cribl, Gitlab"]
        emoji_to_index = {chr(0x1F1E6 + i): i for i in range(len(companies))}
        if emoji in emoji_to_index:
            idx = emoji_to_index[emoji]
            comp = companies[idx]
            if comp in self.selected_companies:
                self.selected_companies.remove(comp)
            else:
                self.selected_companies.add(comp)
        elif emoji == NEXT_EMOJI:
            await self.add_companies()
        elif emoji == CANCEL_EMOJI:
            await self.cancel_session()

    async def add_companies(self):
        if not self.selected_companies:
            await self.ctx.send("⚠️ Please select at least one company to add.")
            return
        user_prefs = self.ui_system.storage_service.get_user_preferences(self.ctx.author.id)
        for comp in self.selected_companies:
            user_prefs.add_company(comp)
        self.ui_system.storage_service.save_user_preferences(user_prefs)
        embed = discord.Embed(
            title="✅ Company(ies) Added!",
            description=f"Added: {', '.join(self.selected_companies)}",
            color=0x00ff00
        )
        await self.ctx.send(embed=embed)
        self.ui_system.cleanup_session(self.user_id)

    async def cancel_session(self):
        await self.ctx.send("❌ Add company session cancelled.")
        self.ui_system.cleanup_session(self.user_id)

# Additional session classes for other commands would follow the same pattern 