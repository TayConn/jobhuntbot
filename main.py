#!/usr/bin/env python3
"""
Job Hunt Buddy - Discord Bot
A Discord bot that scrapes job postings from various tech companies
and notifies users based on their preferences.
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.bot.discord_bot import JobHuntBot

async def main():
    """Main entry point for the Job Hunt Bot"""
    bot = JobHuntBot()
    
    try:
        print("🚀 Starting Job Hunt Bot...")
        await bot.start()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Job Hunt Bot...")
        await bot.stop()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        await bot.stop()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 