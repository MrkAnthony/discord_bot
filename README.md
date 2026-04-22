# Discord Mock Interview Bot

A Discord bot that automatically pairs users for mock coding interviews, manages private voice channels, and posts job opportunities.

## 🏗️ Architecture Overview

The project has two independent systems that run separately:

**1. Discord Bot (`main.py`)** — A long-running process that connects to Discord via websocket. It listens for slash commands and voice channel events in real time. This is the core of the application and handles all user-facing interaction: queue management, matchmaking, voice channel creation, and cleanup.

**2. Job Posting Scripts (`scripts/`)** — Standalone Python scripts executed on a schedule by GitHub Actions. They scrape job listings from SimplifyJobs repositories, filter and deduplicate them, and post new listings to Discord channels via webhooks. These scripts have no dependency on the bot process — they run independently and communicate with Discord through webhook URLs, not the bot token.

```
├── main.py                          # Discord bot (long-running process)
├── neetcode_list.py                 # Problem bank imported by main.py
├── scripts/
│   ├── fetch-jobs.py                # Internship job scraper (runs via GitHub Actions)
│   └── fetch-newgrad-jobs.py        # New grad job scraper (runs via GitHub Actions)
├── .github/workflows/
│   ├── post-jobs.yml                # Cron schedule for internship script
│   └── post-newgrad-jobs.yml        # Cron schedule for new grad script
├── posted_jobs_internships.json     # Tracking file — prevents duplicate internship posts
├── posted_jobs_newgrad.json         # Tracking file — prevents duplicate new grad posts
├── .env                             # Local environment variables (not committed)
└── requirements.txt
```

## 🔄 Data Flow

### Bot Matchmaking Flow

```
User runs /join-queue → Bot adds user to in-memory queue (dict by difficulty)
                        → Second user joins same difficulty
                        → Bot pops both from queue
                        → Creates private voice channel (permission-locked to the pair)
                        → DMs both users with a problem link from neetcode_list.py
                        → Auto-moves users already in voice to the new channel

User leaves voice      → on_voice_state_update fires
                        → Bot waits 15 seconds
                        → If channel is empty, deletes it and removes from active_interviews
```

### Job Posting Flow

```
GitHub Actions cron triggers → Runs fetch-jobs.py or fetch-newgrad-jobs.py
                             → Script fetches raw README from the repo
                             → Parses HTML tables with regex for SWE/PM/DS roles
                             → Filters: US-only, 0-3 days old (internships) or 0-4 days (new grad)
                             → Strips tracking params (utm_source, ref) from URLs
                             → Checks job ID against posted_jobs_*.json to skip duplicates
                             → Posts up to 10 new jobs as Discord embeds via webhook
                             → Updates tracking JSON and commits back to repo
```

## 🧠 Key Design Decisions

**In-memory state for the bot** — Queues and active interviews are stored in Python dictionaries, not a database. This keeps things simple but means state is lost on restart. If the bot crashes mid-session, orphaned voice channels may need manual cleanup.

**Regex-based scraping for jobs** — The job scripts parse HTML tables from GitHub README files using regex rather than an HTML parser. This works because the repo follow a consistent table format, but it's brittle if they change their markup, the parsing will break.

**Separate tracking files per job type** — Internships and new grad jobs each have their own JSON tracking file. The new grad script includes a `clean_old_jobs()` function that prunes entries older than 4 days; the internship script currently does not have this cleanup (the cleanup runs in `main.py` instead).

**Webhook-based posting vs. bot-based posting** — Job postings use Discord webhooks rather than the bot's own connection. This means the job scripts can run as stateless CI jobs without needing the bot to be online.

## 📋 Commands

**`/join-queue`** — Join the interview queue with a difficulty selection (Easy/Medium/Hard/Random). Only works in the `#find-partner` channel.

**`/leave-queue`** — Leave the queue. Only works in the `#find-partner` channel.

## 📚 Problem Bank

The bot pulls from a curated list of 57 NeetCode problems defined in `neetcode_list.py`, organized by difficulty:

- **Easy (17)** — Two Sum, Valid Palindrome, Reverse Linked List, Invert Binary Tree, etc.
- **Medium (29)** — 3Sum, LRU Cache, Daily Temperatures, Koko Eating Bananas, etc.
- **Hard (7)** — Trapping Rain Water, Sliding Window Maximum, Merge K Sorted Lists, etc.

Topics covered: Two Pointers, Binary Search, Trees, Stacks, Array + Hashing, Sliding Windows, Linked Lists.

To add new problems, append entries to the appropriate difficulty list in `neetcode_list.py` following the existing `{'name': '...', 'link': '...'}` format.

## ⚙️ Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root:
```env
DISCORD_TOKEN=your_bot_token_here
SIMPLIFY_INTERNSHIP_URL=url_to_internship_readme
SIMPLIFY_NEWGRAD_URL=url_to_newgrad_readme
```

3. Start the bot:
```bash
python main.py
```

For testing, set `TESTING_BOT_CODE` in your `.env` to run against a test server.

## 📂 Environment Variables

| Variable | Description | Used By |
|---|---|---|
| `DISCORD_TOKEN` | Bot token for Discord authentication | `main.py` |
| `TESTING_BOT_CODE` | When set, runs the bot in testing/development mode | `main.py` |
| `SIMPLIFY_INTERNSHIP_URL` | Raw URL to SimplifyJobs internship README | `fetch-jobs.py` |
| `SIMPLIFY_NEWGRAD_URL` | Raw URL to SimplifyJobs new grad README | `fetch-newgrad-jobs.py` |
| `DISCORD_WEBHOOK_URL_INTERNSHIPS` | Production webhook for internship posts | `fetch-jobs.py` |
| `DISCORD_WEBHOOK_URL_INTERNSHIPS_TEST` | Test webhook for internship posts | `fetch-jobs.py` |
| `DISCORD_WEBHOOK_URL_NEWGRAD` | Production webhook for new grad posts | `fetch-newgrad-jobs.py` |
| `DISCORD_WEBHOOK_URL_NEWGRAD_TEST` | Test webhook for new grad posts | `fetch-newgrad-jobs.py` |

## 🤖 Automated Job Postings

### Internship Postings

- **Schedule**: 4x daily at 11 AM, 3 PM, 7 PM, 10 PM EST via GitHub Actions
- **Workflow**: `.github/workflows/post-jobs.yml`
- **Job Types**: Software Engineering, Product Management, Data Science
- **Filters**: US-only, 0–3 days old
- **Tracking**: `posted_jobs_internships.json`
- **Batch Limit**: 10 per run

### New Grad Postings

- **Schedule**: 4x daily at 10 AM, 2 PM, 6 PM, 10 PM EST via GitHub Actions
- **Workflow**: `.github/workflows/post-newgrad-jobs.yml`
- **Job Types**: Software Engineering, Product Management, Data Science
- **Filters**: US-only, 0–4 days old
- **Tracking**: `posted_jobs_newgrad.json`
- **Batch Limit**: 10 per run
- **Auto-Cleanup**: `clean_old_jobs()` prunes tracked jobs older than 4 days

### Setting Up Webhooks

1. In your Discord server: Settings → Integrations → Webhooks → Create webhooks for each job type
2. In your GitHub repo: Settings → Secrets and variables → Actions → Add the webhook URLs as secrets (see `GITHUB_SECRETS_GUIDE.md`)
3. To test: Go to the Actions tab → Select a workflow → Click "Run workflow"

### Customizing Schedules

Edit the cron expressions in the workflow files. Times are in UTC (GitHub Actions requirement).

**Internships** (`.github/workflows/post-jobs.yml`):
```yaml
schedule:
  - cron: '0 16,20,0,4 * * *'  # 11 AM, 3 PM, 7 PM, 11 PM EST
```

**New Grads** (`.github/workflows/post-newgrad-jobs.yml`):
```yaml
schedule:
  - cron: '0 15,19,23,3 * * *'  # 10 AM, 2 PM, 6 PM, 10 PM EST
```

Use [crontab.guru](https://crontab.guru/) to create custom schedules.