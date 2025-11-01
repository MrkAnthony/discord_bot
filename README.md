# Discord Mock Interview Bot

A Discord bot that automatically pairs users for mock coding interviews and manages private voice channels.

## 📁 Main File
`main.py` - All bot logic and commands

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