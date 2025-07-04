#!/usr/bin/env python3
"""
Job Hunt Buddy - Discord Bot
A Discord bot that scrapes job postings from various tech companies
and notifies users based on their preferences.
"""

import asyncio
import sys
import os
import subprocess
import importlib

def check_and_install_dependencies():
    """Check if required dependencies are installed and install them if needed"""
    required_packages = [
        'discord',
        'playwright',
        'beautifulsoup4',
        'requests',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"📦 Installing missing dependencies: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ])
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            sys.exit(1)
    
    # Check if Playwright browsers are installed
    try:
        from playwright.async_api import async_playwright
        # Try to create a browser instance to check if browsers are installed
        print("🌐 Checking Playwright browsers...")
        subprocess.check_call(['playwright', 'install', 'chromium'], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Playwright browsers ready")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📥 Installing Playwright browsers...")
        try:
            subprocess.check_call(['playwright', 'install', 'chromium'])
            print("✅ Playwright browsers installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Playwright browsers: {e}")
            sys.exit(1)

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def main():
    """Main entry point for the Job Hunt Bot"""
    # Check and install dependencies if needed
    check_and_install_dependencies()
    
    from src.bot.discord_bot import JobHuntBot
    
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