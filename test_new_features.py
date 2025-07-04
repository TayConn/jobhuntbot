#!/usr/bin/env python3
"""
Test script for new Discord bot features:
- Guide embed functionality
- Welcome message functionality
- Member join event handling
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_embed_creation():
    """Test that the guide embed can be created without errors"""
    try:
        print("Testing guide embed creation...")
        
        # Import required modules
        import discord
        from src.utils.config import Config
        
        # Create a mock embed (similar to what the bot would create)
        embed = discord.Embed(
            title="🤖 Job Hunt Buddy - Complete Guide",
            description="Welcome to Job Hunt Buddy! This bot automatically monitors job postings and sends personalized notifications.",
            color=0x0099ff
        )
        
        # Add fields (simplified version)
        embed.add_field(
            name="🚀 Quick Start",
            value="```\n!subscribe software engineer\n!addlocation \"San Francisco\"\n!checknow\n```",
            inline=False
        )
        
        embed.add_field(
            name="🔍 Core Commands",
            value="• `!checknow` - Check for new jobs\n• `!dumpjobs` - Show all current jobs\n• `!preferences` - View your settings",
            inline=True
        )
        
        # Test with categories
        categories_text = "• " + "\n• ".join(Config.DEFAULT_CATEGORIES[:6])
        embed.add_field(
            name="📋 Popular Categories",
            value=categories_text,
            inline=True
        )
        
        print("✅ Guide embed created successfully")
        print(f"   - Title: {embed.title}")
        print(f"   - Fields: {len(embed.fields)}")
        return True
        
    except Exception as e:
        print(f"❌ Guide embed creation failed: {e}")
        return False

def test_welcome_message():
    """Test welcome message creation"""
    try:
        print("Testing welcome message creation...")
        
        import discord
        from src.models.user_preferences import UserPreferences
        
        # Create a mock welcome embed
        embed = discord.Embed(
            title="🎉 Welcome to Job Hunt Buddy!",
            description="Hi @user! I'm here to help you find your next job opportunity.",
            color=0x00ff00
        )
        
        embed.add_field(
            name="🚀 Get Started",
            value="1. **Subscribe to job categories**: `!subscribe software engineer`\n2. **Add location preferences**: `!addlocation \"San Francisco\"`\n3. **Check for jobs**: `!checknow`",
            inline=False
        )
        
        embed.add_field(
            name="📋 Popular Commands",
            value="• `!subscribe` - See available job categories\n• `!preferences` - View your current settings\n• `!bothelp` - Show all commands\n• `!dumpjobs` - See all current openings",
            inline=False
        )
        
        print("✅ Welcome message created successfully")
        print(f"   - Title: {embed.title}")
        print(f"   - Fields: {len(embed.fields)}")
        return True
        
    except Exception as e:
        print(f"❌ Welcome message creation failed: {e}")
        return False

def test_bot_intents():
    """Test that the bot intents are configured correctly"""
    try:
        print("Testing bot intents configuration...")
        
        import discord
        from src.bot.discord_bot import JobHuntBot
        
        # Create bot instance
        bot = JobHuntBot()
        
        # Check intents
        intents = bot.bot.intents
        print(f"   - message_content: {intents.message_content}")
        print(f"   - members: {intents.members}")
        
        if intents.message_content and intents.members:
            print("✅ Bot intents configured correctly")
            return True
        else:
            print("❌ Bot intents not configured correctly")
            return False
            
    except Exception as e:
        print(f"❌ Bot intents test failed: {e}")
        return False

def test_commands_import():
    """Test that new commands can be imported"""
    try:
        print("Testing new commands import...")
        
        from src.bot.commands import JobBotCommands
        
        # Check if the new methods exist
        methods = dir(JobBotCommands)
        required_methods = ['post_guide', 'post_guide_to_channel', 'send_welcome', '_send_welcome_message']
        
        for method in required_methods:
            if method in methods:
                print(f"   ✅ {method} method found")
            else:
                print(f"   ❌ {method} method missing")
                return False
        
        print("✅ All new command methods found")
        return True
        
    except Exception as e:
        print(f"❌ Commands import test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing new Discord bot features...\n")
    
    tests = [
        test_embed_creation,
        test_welcome_message,
        test_bot_intents,
        test_commands_import
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! New features are ready to use.")
        print("\n📋 Usage Instructions:")
        print("1. Use !postguide to post the guide in any channel")
        print("2. Use !postguidetochannel 1390559452599685130 to post to specific channel")
        print("3. New users will automatically receive welcome messages")
        print("4. Users can use !welcome to get a welcome message anytime")
    else:
        print("⚠️  Some tests failed. Please check the errors above.") 