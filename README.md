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
- **Multi-company scraping**: Discord, Reddit, Monarch Money
- **Smart filtering**: Location-based (US-only for Reddit), category-based
- **Duplicate prevention**: Tracks seen jobs to avoid spam
- **Real-time notifications**: Posts new jobs immediately to Discord

### 👤 User Preferences System
- **Category subscriptions**: Subscribe to specific job types (e.g., "software engineer", "frontend")
- **Location preferences**: Filter by specific cities or regions
- **Company preferences**: Focus on specific companies
- **Personalized notifications**: Get only jobs that match your criteria

### 🤖 Discord Commands
- `!checknow` - Manually check for new jobs
- `!dumpjobs` - Show all current job listings
- `!subscribe [category]` - Subscribe to job categories
- `!unsubscribe [category]` - Unsubscribe from categories
- `!preferences` - View your current preferences
- `!addlocation [location]` - Add location preference
- `!addcompany [company]` - Add company preference
- `!clearpreferences` - Clear all preferences
- `!help` - Show all available commands

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
├── main.py                # Entry point
├── env.example            # Environment variables template
├── README.md              # This file
├── DISCORD_USAGE_GUIDE.txt # User guide for Discord
├── test_refactor.py       # Test refactored structure
├── test_new_features.py   # Test new Discord features
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
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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

**Optional:**
- `GUIDE_CHANNEL_ID` - Channel where the guide embed is posted (for `!postguidetoconfig`)

## 📋 Available Job Categories

Users can subscribe to these job categories:
- Software Engineer
- Frontend
- Backend
- Full Stack
- Product Manager
- Marketing
- Design
- Data Scientist
- DevOps
- QA/Test Engineer

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

Create a systemd service for automatic startup:

```ini
[Unit]
Description=Job Hunt Buddy Discord Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/jobhuntbuddy
Environment=PATH=/path/to/jobhuntbuddy/venv/bin
ExecStart=/path/to/jobhuntbuddy/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 🧪 Testing

The project includes comprehensive test suites to verify functionality:

### Running Tests

```bash
# Test the refactored structure and imports
python test_refactor.py

# Test new Discord features (embeds, welcome messages, etc.)
python test_new_features.py

# Run both test suites
python test_refactor.py && python test_new_features.py
```

### What Tests Cover

**`test_refactor.py`:**
- ✅ Module imports and dependencies
- ✅ Job model functionality
- ✅ User preferences model functionality
- ✅ Configuration loading
- ✅ Service initialization

**`test_new_features.py`:**
- ✅ Discord embed creation
- ✅ Welcome message generation
- ✅ Bot intents configuration
- ✅ New command methods
- ✅ Guide embed functionality

### Test Output Example

```
🧪 Testing refactored Job Hunt Bot...

Testing imports...
✅ Config imported successfully
✅ Models imported successfully
✅ Scrapers imported successfully
✅ Services imported successfully
✅ Bot imported successfully

🎉 All imports successful! The refactored structure is working.

✅ Job model test passed: Software Engineer at test_company
✅ UserPreferences test passed: 1 categories

📊 Test Results: 3/3 tests passed
🎉 All tests passed! The refactor is ready to use.
```

### Troubleshooting Tests

If tests fail:
1. **Check dependencies**: `pip install -r requirements.txt`
2. **Verify Python version**: Ensure you're using Python 3.11+
3. **Check virtual environment**: Make sure you're in the correct venv
4. **Review error messages**: Tests provide detailed error information

## 📈 Adding New Features

### Development Workflow

1. **Make your changes** in the appropriate module
2. **Run tests** to ensure nothing is broken:
   ```bash
   python test_refactor.py && python test_new_features.py
   ```
3. **Test manually** if needed (e.g., test new Discord commands)
4. **Update documentation** (README, Discord guide, etc.)

### Adding a New Job Scraper

1. Create a new scraper class in `src/scrapers/`
2. Inherit from `BaseScraper`
3. Implement the `scrape_jobs()` method
4. Add the scraper to `JobMonitor.scrapers`
5. **Run tests** to verify the new scraper works

### Adding New Commands

1. Add command methods to `JobBotCommands` in `src/bot/commands.py`
2. Use the `@commands.command()` decorator
3. Update the help command with new command information
4. **Test the new command** in Discord
5. **Update documentation** if needed

### Testing New Features

- **Unit tests**: Add to existing test files or create new ones
- **Integration tests**: Test with actual Discord bot
- **Manual testing**: Test commands and features in Discord

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check the Discord bot logs for error messages
2. Verify your environment variables are set correctly
3. Ensure all dependencies are installed
4. Check that Playwright browsers are installed

---

**Note**: This bot is designed for personal use and educational purposes. Please respect the terms of service of the websites being scraped.
