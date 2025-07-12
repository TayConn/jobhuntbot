# Job Hunt Buddy 🤖

A smart Discord bot that automatically scrapes job postings from tech company career pages and notifies users based on their personalized preferences.

## 🚀 Quick Start

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Configure
cp env.example .env
# Edit .env with your Discord tokens and channel IDs

# Test
python test_refactor.py && python test_new_features.py

# Run
python main.py
```

## ✨ Features

### 🔍 Job Monitoring
- **Multi-company scraping**: Discord, Reddit, Monarch Money, Cribl, GitLab
- **Smart filtering**: Location-based (US-only for Reddit), category-based, experience-based, salary-based
- **Duplicate prevention**: Tracks seen jobs to avoid spam
- **Real-time notifications**: Posts new jobs immediately to Discord

### 👤 User Preferences System
- **Category subscriptions**: Subscribe to specific job types (e.g., "software engineer", "frontend", "data scientist")
- **Location preferences**: Filter by specific cities or regions
- **Company preferences**: Focus on specific companies
- **Experience level filtering**: Filter by entry, junior, mid, senior, lead levels
- **Salary range filtering**: Filter by salary ranges from 0-50k to 300k+
- **Work arrangement filtering**: Filter by remote, hybrid, or onsite positions
- **Priority alerts**: Get immediate notifications for dream companies and roles
- **Personalized notifications**: Get only jobs that match your criteria

### 🤖 Discord Commands
- `!checknow` - Manually check for new jobs
- `!dumpjobs` - Show all current job listings with advanced filtering
- `!subscribe` - Subscribe to job categories
- `!unsubscribe` - Unsubscribe from categories
- `!preferences` - View your current preferences
- `!addlocation` - Add location preference
- `!addcompany` - Add company preference
- `!addexperience` - Add experience level preference
- `!addsalary` - Add salary range preference
- `!addwork` - Add work arrangement preference
- `!addprioritycompany` - Add priority company for immediate alerts
- `!addprioritycategory` - Add priority category for immediate alerts
- `!setminsalary` - Set minimum salary requirement
- `!setnotifications` - Set notification frequency
- `!setnotificationtime` - Set daily notification time
- `!clearpreferences` - Clear all preferences
- `!bothelp` - Show all available commands

For privacy, DM the bot directly to set your job preferences and use personal commands (like !subscribe, !preferences, etc.).

## 🏗️ Project Structure

The bot is built with a modular, scalable architecture:

```
jobhuntbuddy/
├── src/                    # Modular source code
│   ├── bot/               # Discord bot setup & commands
│   │   ├── __init__.py
│   │   ├── discord_bot.py # Main bot class
│   │   └── commands.py    # Bot command handlers
│   ├── scrapers/          # Job scraping modules
│   │   ├── __init__.py
│   │   ├── base_scraper.py    # Abstract base class
│   │   ├── discord_scraper.py # Discord jobs
│   │   ├── reddit_scraper.py  # Reddit jobs
│   │   └── monarch_scraper.py # Monarch jobs
│   ├── models/            # Data models
│   │   ├── __init__.py
│   │   ├── job.py             # Job data model
│   │   └── user_preferences.py # User preferences model
│   ├── services/          # Business logic
│   │   ├── __init__.py
│   │   ├── job_monitor.py     # Main monitoring logic
│   │   ├── notification_service.py # Discord notifications
│   │   └── storage_service.py # Job storage & preferences
│   └── utils/             # Configuration & utilities
│       ├── __init__.py
│       └── config.py          # Configuration management
├── data/                  # Persistent storage
│   ├── seen_jobs.json     # Tracked job URLs
│   └── user_preferences.json # User preference settings
├── tests/
│   ├── dev_structure_tests.py #Simple test script to verify the code is working as expected before running
│   └── dev_feature_tests.py #tests new bot features and commands
├── main.py                # Entry point
├── env.example            # Environment variables template
├── README.md              # This file
├── DISCORD_USAGE_GUIDE.txt # User guide for Discord
└── requirements.txt       # Python dependencies
```

## 🛠️ Tech Stack

- **Python 3.11+** - Core language
- **discord.py** - Discord API integration
- **Playwright** - Web scraping for JavaScript-rendered content
- **BeautifulSoup** - HTML parsing
- **GitHub Actions** - CI/CD pipeline for auto-deployment

## 🚀 Setup & Installation

### Prerequisites
- Python 3.11 or higher
- Discord Bot Token
- Discord Channel ID

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd jobhuntbuddy
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**
   ```bash
   playwright install chromium
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Discord bot token and channel ID
   ```

6. **Run the bot**
   ```bash
   python main.py
   ```

### Environment Variables

Create a `.env` file in the project root:

```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
MAIN_CHANNEL_ID=channel_for_bot_job_postings
GUIDE_CHANNEL_ID=channel_for_bot_usage_instructions
```

**Required:**
- `DISCORD_BOT_TOKEN` - Your Discord bot token
- `MAIN_CHANNEL_ID` - Channel where job notifications are posted and users join
- `GUIDE_CHANNEL_ID` - Channel where the guide embed is posted (for `!postguide` and user onboarding)

## 📋 Available Job Categories

Users can subscribe to these job categories:

### Core Engineering
- Software Engineer, Frontend, Backend, Full Stack, Web Developer, Mobile Developer

### Specialized Engineering  
- Data Engineer, Data Scientist, Machine Learning Engineer, AI Engineer, DevOps Engineer, Security Engineer, Cloud Engineer, Platform Engineer, QA Engineer, Test Engineer

### Product & Design
- Product Manager, UX Designer, UI Designer, Product Designer, Visual Designer

### Management & Leadership
- Engineering Manager, Tech Lead, Project Manager, Program Manager, Scrum Master

### Business & Marketing
- Marketing Manager, Digital Marketing, Growth Marketing, Sales Engineer, Customer Success, Business Analyst

### Operations & Support
- Customer Support, Technical Support, Operations Manager, Business Operations

## 🎯 Experience Levels
- Entry Level, Junior, Mid Level, Senior, Lead, Principal, Staff, Director, VP, CTO, Executive

## 💰 Salary Ranges
- 0-50k, 50k-75k, 75k-100k, 100k-125k, 125k-150k, 150k-175k, 175k-200k, 200k-250k, 250k-300k, 300k+

## 🏠 Work Arrangements
- Remote, Hybrid, Onsite, In Office, Work From Home

## 🔧 Configuration

The bot's behavior can be customized in `src/utils/config.py`:

- **Job check interval**: How often to check for new jobs (default: 2 hours)
- **Scraper timeout**: Maximum time to wait for page loads (default: 60 seconds)
- **Default categories**: Available job categories for subscription
- **Supported companies**: Companies to scrape jobs from

## 🚀 Deployment

### GitHub Actions (Recommended)

The project includes a GitHub Actions workflow for automatic deployment to a Raspberry Pi or other server:

1. Set up a self-hosted runner on your server
2. Configure the workflow in `.github/workflows/deploy.yml`
3. Push to the `main` branch to trigger deployment

### Manual Deployment

1. **Upload files to your server**
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
3. **Set up environment variables**
4. **Run the bot**
   ```bash
   python main.py
   ```

### Systemd Service (Linux)

#### Option 1: Simple Service (Manual Dependency Management)
Create a systemd service for automatic startup:

```ini
[Unit]
Description=Job Hunt Buddy Discord Bot
After=network.target

[Service]
Type=simple
User=taylor
WorkingDirectory=/path/to/your/project
Environment=PATH=/path/to/your/project/venv/bin
ExecStart=/path/to/your/project/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Option 2: Auto-Dependency Management Service
Use the provided service file that automatically handles dependencies:

```bash
# Copy the service file
sudo cp deploy/jobhuntbot.service /etc/systemd/system/

# Make the install script executable
chmod +x deploy/install_dependencies.sh

# Reload and enable the service
sudo systemctl daemon-reload
sudo systemctl enable jobhuntbot
sudo systemctl start jobhuntbot
```

#### Option 3: Python-Based Auto-Dependency (Recommended)
The bot now automatically checks and installs missing dependencies on startup. Just use the simple service file above - the bot will handle dependency management internally.

**Benefits:**
- ✅ No manual dependency installation needed
- ✅ Automatic updates when requirements.txt changes
- ✅ Works across different deployment environments
- ✅ Graceful error handling and logging

## Server Onboarding & Verification

- 1. Create a "guide" channel for onboarding. This channel will be used for the bot's terms message and user verification.
- 2. Set up the verified role in your server.
