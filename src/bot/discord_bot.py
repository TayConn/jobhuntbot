import discord
import asyncio
from discord.ext import commands
from datetime import datetime
from ..services.job_monitor import JobMonitor
from ..services.notification_service import NotificationService
from ..services.storage_service import StorageService
from .commands import JobBotCommands
from ..utils.config import Config

class JobHuntBot:
    """Main Discord bot for job hunting"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True  # Required for on_member_join events
        
        self.bot = commands.Bot(command_prefix="!", intents=intents)
        
        # Initialize services
        self.notification_service = NotificationService(self.bot, Config.MAIN_CHANNEL_ID)
        self.job_monitor = JobMonitor(self.notification_service)
        self.storage_service = StorageService()
        
        # Setup event handlers
        self.setup_events()
    
    def setup_events(self):
        """Setup Discord bot event handlers"""
        
        @self.bot.event
        async def on_ready():
            if not hasattr(self.bot, "monitor_started"):
                print(f'🤖 Welcome to Job Hunt Bot!')
                print(f'✅ Logged in as {self.bot.user}')
                print(f"[{datetime.now()}] ✅ Bot ready. Starting job monitoring...")
                
                self.bot.monitor_started = True
                # Start the background monitoring task
                self.bot.bg_task = asyncio.create_task(self.job_monitor.monitor_loop())
        
        @self.bot.event
        async def on_command_error(ctx, error):
            """Handle command errors"""
            if isinstance(error, commands.CommandNotFound):
                await ctx.send("❌ Command not found. Use `!help` to see available commands.")
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send(f"❌ Missing required argument: {error.param}")
            else:
                await ctx.send(f"❌ An error occurred: {error}")
                print(f"[ERROR] Command error: {error}")
        
        @self.bot.event
        async def on_member_join(member):
            """Send welcome message when a new member joins"""
            print(f"[INFO] New member joined: {member.name} ({member.id})")
            
            # Check if we should send welcome message (if MAIN_CHANNEL_ID is configured)
            from ..utils.config import Config
            if Config.MAIN_CHANNEL_ID != 0:
                # Only send welcome if member joined the main channel
                # Note: This is a simplified check - in practice, all members join the guild
                # You might want to add more specific logic based on your server setup
                print(f"[INFO] Main channel configured: {Config.MAIN_CHANNEL_ID}")
            
            # Get the commands cog to access the welcome message function
            commands_cog = self.bot.get_cog('JobBotCommands')
            if commands_cog:
                success = await commands_cog._send_welcome_message(member)
                if success:
                    print(f"[INFO] Welcome message sent to {member.name}")
                else:
                    print(f"[INFO] Could not send welcome message to {member.name} (DMs disabled)")
    
    async def setup_commands(self):
        """Setup Discord bot commands"""
        # Add the commands cog
        await self.bot.add_cog(JobBotCommands(self.bot, self.job_monitor, self.notification_service))
    
    async def start(self):
        """Start the Discord bot"""
        try:
            # Validate configuration
            Config.validate()
            
            # Setup commands
            await self.setup_commands()
            
            # Start the bot
            await self.bot.start(Config.DISCORD_BOT_TOKEN)
        except Exception as e:
            print(f"[ERROR] Failed to start bot: {e}")
            raise
    
    async def stop(self):
        """Stop the Discord bot"""
        if hasattr(self.bot, 'bg_task'):
            self.bot.bg_task.cancel()
        
        await self.bot.close() 