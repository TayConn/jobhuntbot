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
        # Note: members intent disabled to avoid privileged intent requirement
        # Welcome messages can still be sent manually with !welcome command
        
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
        async def on_guild_join(guild):
            """Post the guide embed to the configured guide channel when the bot is added to a server"""
            try:
                channel = guild.get_channel(Config.GUIDE_CHANNEL_ID)
                if not channel:
                    # Try to find a text channel the bot can send to
                    for c in guild.text_channels:
                        if c.permissions_for(guild.me).send_messages:
                            channel = c
                            break
                if channel:
                    # Import the guide embed logic from the commands cog
                    commands_cog = self.bot.get_cog('JobBotCommands')
                    if commands_cog:
                        await commands_cog.post_guide_to_config(await self.bot.get_context(await channel.send("Setting up Job Hunt Buddy...")))
                else:
                    print(f"[ERROR] Could not find a suitable channel to post the guide in guild {guild.name}")
            except Exception as e:
                print(f"[ERROR] Failed to post guide on guild join: {e}")

        @self.bot.event
        async def on_command_error(ctx, error):
            """Handle command errors"""
            if isinstance(error, commands.CommandNotFound):
                await ctx.send("❌ Command not found. Use `!bothelp` to see available commands.")
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send(f"❌ Missing required argument: {error.param}")
            else:
                await ctx.send(f"❌ An error occurred: {error}")
                print(f"[ERROR] Command error: {error}")
        
        @self.bot.command()
        @commands.has_permissions(manage_guild=True)
        async def postterms(ctx):
            """Post the onboarding terms message in the guide channel."""
            channel = ctx.guild.get_channel(Config.GUIDE_CHANNEL_ID)
            if not channel:
                await ctx.send("❌ Could not find the guide channel.")
                return
            terms_text = (
                "**Welcome to Job Hunt Buddy!**\n\n"
                "**Server Rules:**\n"
                "1. **Be Respectful:** Treat all members with respect. No harassment, hate speech, or discrimination of any kind.\n"
                "2. **Keep It Professional:** This is a job-focused community. Please keep discussions relevant to job hunting, career growth, and professional development.\n"
                "3. **No Spam or Self-Promotion:** Do not spam channels or DM members unsolicited offers, advertisements, or promotions.\n"
                "4. **Protect Privacy:** Do not share personal information (yours or others's) publicly. Use DMs for sensitive topics, and never share anyone's private info without consent.\n"
                "5. **Follow Discord's Terms of Service:** All activity must comply with Discord's Terms of Service and Community Guidelines.\n"
                "6. **Use Channels Appropriately:** Post in the correct channels. Job preferences and personal commands should be sent via DM to the bot for privacy.\n"
                "7. **No NSFW or Inappropriate Content:** This is a professional space. Keep all content safe for work.\n"
                "8. **Listen to Staff:** Moderators and admins are here to help. Please follow their instructions.\n\n"
                "By clicking ✅, you acknowledge and agree to follow these rules. Failure to comply may result in removal from the server."
            )
            msg = await channel.send(terms_text)
            await msg.add_reaction("✅")
            # Save message ID for verification
            import json
            with open("terms_message_id.json", "w") as f:
                json.dump({"message_id": msg.id}, f)
            await ctx.send(f"✅ Terms message posted and ready for onboarding!")

        @self.bot.event
        async def on_raw_reaction_add(payload):
            # Handle onboarding verification
            import json
            # Only care about the guide channel and the terms message
            try:
                with open("terms_message_id.json", "r") as f:
                    data = json.load(f)
                    terms_message_id = data["message_id"]
            except Exception:
                terms_message_id = None
            
            if (
                payload.channel_id == Config.GUIDE_CHANNEL_ID and
                terms_message_id and
                payload.message_id == terms_message_id and
                str(payload.emoji) == "✅"
            ):
                guild = self.bot.get_guild(payload.guild_id)
                if not guild:
                    return
                member = guild.get_member(payload.user_id)
                if not member or member.bot:
                    return
                # Assign the 'verified' role
                role = discord.utils.get(guild.roles, name="verified")
                if not role:
                    print("[ERROR] 'verified' role not found.")
                    return
                try:
                    await member.add_roles(role, reason="Accepted terms in guide channel")
                    # DM welcome message
                    try:
                        await member.send(
                            "🎉 You are now verified and have access to the main channels! Welcome to the server."
                        )
                    except Exception:
                        print(f"[INFO] Could not DM user {member.display_name} after verification.")
                except Exception as e:
                    print(f"[ERROR] Could not assign verified role: {e}")
            
            # Handle interactive UI reactions
            commands_cog = self.bot.get_cog('JobBotCommands')
            if commands_cog and hasattr(commands_cog, 'interactive_ui'):
                await commands_cog.interactive_ui.handle_reaction(payload)

        @self.bot.event
        async def on_message(message):
            # Let the interactive UI handle custom location input
            commands_cog = self.bot.get_cog('JobBotCommands')
            if commands_cog and hasattr(commands_cog, 'interactive_ui'):
                await commands_cog.interactive_ui.handle_message(message)
            # Continue processing commands as normal
            await self.bot.process_commands(message)

        # Note: on_member_join event removed due to privileged intent requirement
        # Users can still get welcome messages using the !welcome command
    
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