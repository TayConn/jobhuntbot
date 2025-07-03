import discord
import requests
from bs4 import BeautifulSoup
import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN =  os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

print(f"[DEBUG] Token starts with: {TOKEN[:5]}")


intents = discord.Intents.default()
intents.message_content = True
from discord.ext import commands
bot = commands.Bot(command_prefix="!", intents=intents)

SEEN_JOBS_FILE = "seen_jobs.json"

def load_seen_jobs():
    try:
        with open(SEEN_JOBS_FILE, "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_seen_jobs(seen_jobs):
    with open(SEEN_JOBS_FILE, "w") as f:
        json.dump(list(seen_jobs), f)

async def scrape_discord_jobs():
    jobs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://discord.com/careers", timeout=60000)
        await page.wait_for_load_state("networkidle")

        job_cards = await page.query_selector_all("a.job-item.w-inline-block")

        for card in job_cards:
            try:
                title_elem = await card.query_selector("h3")
                location_elem = await card.query_selector("p")
                href = await card.get_attribute("href")

                title = await title_elem.inner_text() if title_elem else "N/A"
                location = await location_elem.inner_text() if location_elem else "N/A"
                link = f"https://discord.com{href}" if href else ""

                jobs.append((title.strip(), link.strip(), location.strip(), []))
            except Exception as e:
                print(f"[DEBUG] Failed to parse a Discord job card: {e}")

        await browser.close()
    return jobs

async def scrape_reddit_jobs(full_dump=False):
    jobs = []
    base_url = "https://boards.greenhouse.io/reddit"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(base_url, timeout=60000)
        await page.wait_for_load_state("networkidle")

        while True:
            job_rows = await page.query_selector_all("tr.job-post")

            for row in job_rows:
                try:
                    a_tag = await row.query_selector("a[href*='/reddit/jobs/']")
                    title_p = await row.query_selector("p.body--medium")
                    location_p = await row.query_selector("p.body--metadata")

                    title = await title_p.inner_text() if title_p else "N/A"
                    href = await a_tag.get_attribute("href") if a_tag else ""
                    location = await location_p.inner_text() if location_p else "N/A"
                    full_link = href if href.startswith("http") else f"https://boards.greenhouse.io{href}"

                    if "united states" not in location.lower():
                        continue  # ✅ skip non-U.S. jobs

                    #print(f"[DEBUG] Found Reddit job: {title} | {location}")

                    if full_dump:
                        jobs.append((title.strip(), full_link.strip(), location.strip()))
                    else:
                        if any(role in title.lower() for role in ["marketing", "product manager", "software engineer", "frontend", "front end", "web"]):
                            jobs.append((title.strip(), full_link.strip(), location.strip()))
                except Exception as e:
                    print(f"[DEBUG] Error parsing Reddit job: {e}")

            # Handle pagination
            next_button = await page.query_selector("a.next_page")
            is_disabled = await next_button.get_attribute("class") if next_button else "disabled"
            if not next_button or "disabled" in is_disabled:
                break

            await next_button.click()
            await page.wait_for_load_state("networkidle")

        await browser.close()

    return jobs

async def scrape_monarch_jobs():
    jobs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://jobs.ashbyhq.com/monarchmoney", timeout=60000)
        await page.wait_for_load_state("networkidle")

        job_links = await page.query_selector_all("a[href^='/monarchmoney/']")

        for link in job_links:
            title = await link.inner_text()
            href = await link.get_attribute("href")
            parent = await link.evaluate_handle("el => el.closest('div')")

            location = "N/A"
            if parent:
                full_text = await parent.inner_text()
                location = full_text.replace(title, "").strip()

            jobs.append((title.strip(), "https://jobs.ashbyhq.com" + href, location.strip()))

        await browser.close()
    return jobs


async def send_job_to_discord(title, link):
    channel = await bot.fetch_channel(CHANNEL_ID)
    if channel:
        await channel.send(f"📢 **New Job Posted!**\n**{title}**\n{link}\n🕓 {datetime.now().strftime('%Y-%m-%d %H:%M')}")

async def job_monitor_loop():
    await bot.wait_until_ready()
    seen_jobs = load_seen_jobs()
    channel = await bot.fetch_channel(CHANNEL_ID)

    while not bot.is_closed():
        await run_job_scrapers(send_to_channel=channel)

        print(f"[{datetime.now()}] Checked for jobs. Sleeping for 2 hours.")
        await asyncio.sleep(7200)

async def run_job_scrapers(send_to_channel):
    seen_jobs = load_seen_jobs()
    new_jobs = []

    # async: Reddit
    try:
        reddit_jobs = await scrape_reddit_jobs(full_dump=True)
        for title, link, location in reddit_jobs:
            #print(f"[DEBUG] Reddit: {title} – {link}")
            if link not in seen_jobs:
                new_jobs.append((title, link))
                seen_jobs.add(link)
            # else:
            #     print("[DEBUG] → Already seen (Reddit)")
    except Exception as e:
        print(f"[ERROR] Reddit scraper failed: {e}")

    # Async: Discord
    try:
        discord_jobs = await scrape_discord_jobs()
        for title, link, location, tags in discord_jobs:
            #print(f"[DEBUG] Discord: {title} – {link}")
            if link not in seen_jobs:
                new_jobs.append((title, link))
                seen_jobs.add(link)
            # else:
            #     print("[DEBUG] → Already seen (Discord)")
    except Exception as e:
        print(f"[ERROR] Discord scraper failed: {e}")

    # Async: Monarch
    try:
        monarch_jobs = await scrape_monarch_jobs()
        for title, link, location in monarch_jobs:
            #print(f"[DEBUG] Monarch: {title} – {link}")
            if link not in seen_jobs:
                new_jobs.append((title, link))
                seen_jobs.add(link)
            # else:
            #     print("[DEBUG] → Already seen (Monarch)")
    except Exception as e:
        print(f"[ERROR] Monarch scraper failed: {e}")

    # Send messages
    if new_jobs:
        for title, link in new_jobs:
            await send_to_channel.send(f"📢 **New Job Posted!**\n**{title}**\n{link}\n🕓 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    else:
        await send_to_channel.send("🤖 Checked for jobs — no new listings this time!")

    save_seen_jobs(seen_jobs)
    print(f"[DEBUG] ✅ Saved seen jobs.")

@bot.event
async def on_ready():
    if not hasattr(bot, "monitor_started"):
        print(f'✅ Logged in as {bot.user}')
        print(f"[{datetime.now()}] ✅ Job check complete. Next run in 2 hours.")
        bot.monitor_started = True
        bot.bg_task = asyncio.create_task(job_monitor_loop())

@bot.command(name="checknow")
async def check_now_command(ctx):
    await ctx.send("🔍 Checking for new jobs now...")
    await run_job_scrapers(send_to_channel=ctx.channel)

@bot.command(name="dumpjobs")
async def dump_jobs_command(ctx):
    await ctx.send("🕵️ Scraping all current job listings (this may take a few seconds)...")

    discord_jobs = await scrape_discord_jobs()
    monarch_jobs = await scrape_monarch_jobs()
    reddit_jobs = await scrape_reddit_jobs()
    # print(f"[DEBUG] Discord jobs: {len(discord_jobs)}")
    # print(f"[DEBUG] Monarch jobs: {len(monarch_jobs)}")
    # print(f"[DEBUG] Reddit jobs: {len(reddit_jobs)}")

    message = "**🧾 Current Openings:**\n\n"

    def format_jobs_txt(title, jobs):
        if not jobs:
            return f"{title}\n• No jobs found\n\n"
        lines = [f"{title}"]
        for job in jobs:
            job_title = job[0]
            job_link = job[1] if len(job) > 1 else ""
            job_location = job[2] if len(job) > 2 else "N/A"
            lines.append(f"• {job_title} — {job_location}\n  {job_link}")
        return "\n".join(lines) + "\n\n"

    message += format_jobs_txt("Discord", discord_jobs)
    message += format_jobs_txt("Reddit", reddit_jobs)
    message += format_jobs_txt("Monarch Money", monarch_jobs)

    if len(message) < 2000:
        await ctx.send(message)
    else:
        # Save to temporary file
        file_path = "job_dump.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(message)

        await ctx.send("📄 This list is too powerful. View it in a text file:", file=discord.File(file_path))

async def main():
    async with bot:
        await bot.start(TOKEN)

asyncio.run(main())

