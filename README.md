# Discord Mock Interview Bot

A Discord bot that automatically pairs users for mock coding interviews, manages private voice channels, and posts job opportunities.

## 📁 Main Files
- `main.py` - All bot logic and commands
- `scripts/fetch-jobs.py` - Automated internship job posting
- `scripts/fetch-newgrad-jobs.py` - Automated new grad job posting

## 🎯 How It Works

### Queue & Matching
- Users run `/join-queue` in `#find-partner` and select difficulty (Easy/Medium/Hard/Random)
- When 2 users join the same difficulty queue, they're automatically matched
- Bot creates a private voice channel and DMs both users

### Private Interview Rooms
- Only the matched pair can see/join the channel
- Users already in voice are auto-moved; others get a DM link
- All sessions tracked in `active_interviews` dictionary

### Auto-Cleanup
- When someone leaves the voice channel, bot waits 15 seconds
- If channel is still empty, it's deleted automatically
- Handled by `on_voice_state_update()` event

## 📋 Commands

**`/join-queue`** - Join interview queue (Easy/Medium/Hard/Random)  
**`/leave-queue`** - Leave the queue

Both commands only work in `#find-partner` channel.

## ⚙️ Setup

1. Install dependencies:
```bash
   pip install -r requirements.txt
```

2. Create `.env` file:
```env
   DISCORD_TOKEN=your_bot_token_here
```

3. For the bot turn online:
```bash
   python main.py
```

## 🤖 Automated Job Postings

### Internship Postings
- **Source**: [SimplifyJobs Summer 2026 Internships](https://github.com/SimplifyJobs/Summer2026-Internships)
- **Schedule**: Runs every few hours via GitHub Actions (see `.github/workflows/post-jobs.yml`)
- **Job Types**: Software Engineering, Product Management, Data Science
- **Tracking**: `posted_jobs_internships.json` prevents duplicate posts
- **Freshness**: Only posts jobs 0-3 days old

### New Grad Postings
- **Source**: [SimplifyJobs New Grad Positions](https://github.com/SimplifyJobs/New-Grad-Positions)
- **Schedule**: Runs 5 times daily at 9 AM, 11 AM, 3 PM, 7 PM, and 11 PM EST
- **Job Types**: Software Engineering, Product Management, Data Science
- **Tracking**: `posted_jobs_newgrad.json` prevents duplicate posts
- **Freshness**: Only posts jobs 0-4 days old
- **Auto-Cleanup**: Jobs older than 4 days are automatically removed from tracking
- **Test Mode**: Automatically posts to test server when running locally or in GitHub Actions

### Setting Up Job Posting Webhooks

1. **Create Discord Webhook(s)**:
   - Go to your Discord server settings → Integrations → Webhooks
   - Create separate webhooks for internships and new grad jobs (or use the same one)
   - Copy the webhook URLs

2. **Configure GitHub Secrets**:
   - Go to your repository → Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `DISCORD_WEBHOOK_URL` - For internship postings (production)
     - `DISCORD_WEBHOOK_URL_NEWGRAD` - For new grad postings (production)
     - `DISCORD_WEBHOOK_URL_TEST` - For internship postings (testing)
     - `DISCORD_WEBHOOK_URL_NEWGRAD_TEST` - For new grad postings (testing)
     - `ADMIN_PAT` - GitHub Personal Access Token with repo write permissions
   - See `GITHUB_SECRETS_GUIDE.md` for detailed instructions

3. **Manual Trigger**:
   - Go to Actions tab in your GitHub repository
   - Select either workflow: `fetching-job-postings` or `fetch-newgrad-job-postings`
   - Click "Run workflow" to test immediately

### Customizing Job Posting Schedule

Edit the cron expressions in the workflow files:

**Internships** (`.github/workflows/post-jobs.yml`):
```yaml
schedule:
  - cron: '37 16,19,22,1 * * *'  # Currently: 4 times daily
```

**New Grads** (`.github/workflows/post-newgrad-jobs.yml`):
```yaml
schedule:
  - cron: '0 14,16,20 * * *'  # 9 AM, 11 AM, 3 PM EST
  - cron: '0 0,4 * * *'        # 7 PM, 11 PM EST
```

**Note:** Times shown are EST. GitHub Actions runs on UTC, so schedules are automatically converted.

Use [crontab.guru](https://crontab.guru/) to create custom schedules.