# Job Hunt Bot 🤖

This is a Discord bot that tracks job postings from several company careers pages and posts new listings to a Discord channel.

## Features

- ✅ Monitors job boards from:
  - Discord (discord.com/careers)
  - Reddit (Greenhouse)
  - Monarch Money (AshbyHQ)
- 🕵️ Filters jobs by location (e.g., United States only)
- 💬 Responds to `!checkjobs` command in Discord
- 📦 Uses Playwright for JavaScript-rendered content
- 🔄 CI/CD pipeline for auto-deploying updates to a Raspberry Pi
- 📁 Environment variables securely managed via `.env` file

## Tech Stack

- Python 3
- Playwright
- BeautifulSoup
- `discord.py`
- GitHub Actions (CI/CD to Raspberry Pi)

## Local Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python job_hunt_bot.py


## Set up .env
`nano .env`
```DISCORD_BOT_TOKEN=your_token_here
DISCORD_CHANNEL_ID=your_channel_id_here```

## CI/CD pipeline
If desired, set up a GitHub Actions CI/CD pipeline to run the jobs straight to your server running the bot. 
