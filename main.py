'''
TODO:
1. Cleaning up the room after someone leaves
2. Providing questions from Neetcode 150 (2 questions each with link and name of the problem)
3. and assigning random roles (Interviewer or Candidate)
'''

import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()

# To access member info when pairing
intents.members = True

# To move users to voice channels
intents.voice_states = True

# Only if using prefix commands
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Storing my users waiting to be matched with someone else
queue = {
    'easy': [],
    'medium': [],
    'hard': []
}
# store the active interview sessions
active_interviews = {}


# Ensuring that bot is online
@bot.event
async def on_ready():
    print(f'{bot.user.name} I am ready to facilitate learning')
    try:
        synced = await bot.tree.sync()
        print(f'✅ Synced {len(synced)} command(s)')
        for cmd in synced:
            print(f'  - /{cmd.name}')
    except Exception as e:
        print(f'Failed to sync commands: {e}')


@bot.tree.command(name='join-queue', description="Joining the interview queue")
@app_commands.describe(difficulty='Choose a difficultly')
@app_commands.choices(difficulty=[
    app_commands.Choice(name="Easy", value="easy"),
    app_commands.Choice(name="Medium", value="medium"),
    app_commands.Choice(name="Hard", value="hard"),
    app_commands.Choice(name='Random', value='random')
    # Joining Queue Mechanism
])
# joining mock interview queue: /join-queue
async def join_queue(interaction: discord.Interaction, difficulty: app_commands.Choice[str]):
    user = interaction.user
    diff = difficulty.value

    ALLOWED_CHANNEL = 1433269455500087297  # Channel Find-Partner

    if interaction.channel.id != ALLOWED_CHANNEL:
        await interaction.response.send_message(
            f"Please use this command in #find-partner!",
            ephemeral=True
        )
        return

    for queue_name, queue_list in queue.items():
        display_name = difficulty.name
        if user in queue_list:
            await interaction.response.send_message(
                f"You're already in the queue! Use `/leave-queue` to leave first.",
                ephemeral=True
            )
            return

    if diff == "random":
        diff = random.choice(['easy', 'medium', 'hard'])
        chosen_name = diff.capitalize()

        queue[diff].append(user)

        await interaction.response.send_message(
            f"🎲 Random difficulty chosen: **{chosen_name}**\n"
            f"✅ You've joined the **{chosen_name}** queue!\n"
            f"👥 Currently {len(queue[diff])} people waiting.\n"
            f"You'll be notified when matched!",
            ephemeral=True
        )
    else:
        display_name = difficulty.name
        queue[diff].append(user)
        await interaction.response.send_message(
            f"You've joined the **{display_name}** queue!\n"
            f"👥 Currently {len(queue[diff])} people waiting.\n"
            f"You'll be notified when matched!",
            ephemeral=True
        )
    await try_match(interaction.guild, diff)


# Drop the queue command: /leave-queue
@bot.tree.command(name="leave-queue", description="Leave the interview queue")
async def leave_queue(interaction: discord.Interaction):
    user = interaction.user

    ALLOWED_CHANNEL = 1433269455500087297

    if interaction.channel.id != ALLOWED_CHANNEL:
        await interaction.response.send_message(
            f"Please use this command in #find-partner!",
            ephemeral=True
        )
        return

    # Search through all queues
    for diff, queue_list in queue.items():
        if user in queue_list:
            queue_list.remove(user)
            await interaction.response.send_message(
                f"You've left the **{diff.capitalize()}** queue.",
                ephemeral=True
            )
            print(f'{user.name} dropped from {diff} queue')
            return

    await interaction.response.send_message(
        "You're not in any queue!",
        ephemeral=True
    )


async def try_match(guild, difficulty):
    if len(queue[difficulty]) >= 2:
        # Get two random users from queue
        user1 = queue[difficulty].pop(random.randint(0, len(queue[difficulty]) - 1))
        user2 = queue[difficulty].pop(random.randint(0, len(queue[difficulty]) - 1))

        await create_interview_room(guild, user1, user2, difficulty)


async def create_interview_room(guild, user1, user2, difficulty):
    INTERVIEW_ROOM_CATEGORY_ID = 1433270003419058279
    category = guild.get_channel(INTERVIEW_ROOM_CATEGORY_ID)

    if not category:
        print("This wasn't found")
        return None

    overwrite = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),  # Hide from everyone
        user1: discord.PermissionOverwrite(view_channel=True, connect=True),  # Allow user1
        user2: discord.PermissionOverwrite(view_channel=True, connect=True),  # Allow user2
        guild.me: discord.PermissionOverwrite(view_channel=True, connect=True, move_members=True)  # Bot permissions
    }

    try:
        interview_channel = await guild.create_voice_channel(
            name=f"mock interview - {difficulty}",
            category=category,
            overwrites=overwrite,
            reason=f"mock interview room for {user1.name} and {user2.name}"
        )

        print(f"The {interview_channel} was created")

        if user1.voice:
            await user1.move_to(interview_channel)
            print(f"{user1.name} was moved to interview channel")
        else:
            try:
                await user1.send(f"Interview Ready - Good luck! {interview_channel.mention}")
            except discord.Forbidden:
                print(f"Couldn't DM {user1.name} (DMs Disabled)")

        if user2.voice:
            await user2.move_to(interview_channel)
            print(f"{user2.name} was moved to interview channel")
        else:
            try:
                await user2.send(f"Interview Ready - Good luck! {interview_channel.mention}")
            except discord.Forbidden:
                print(f"Couldn't DM {user2.name} (DMs Disabled)")

        # Store in active interviews for tracking
        interview_id = f"{user1.id}_{user2.id}"
        active_interviews[interview_id] = {
            'channel': interview_channel,
            'users': [user1, user2],
            'difficulty': difficulty,
            'start_time': discord.utils.utcnow()
        }
        return interview_channel

    except discord.Forbidden:
        print("Bot lacks permission to create channels or move members")
        return None
    except Exception as e:
        print(f"Error creating interview room: {e}")
        return None


@bot.event
async def on_member_join(member):
    await member.send(
        f"🎯 Welcome, {member.name}! Ready to level up your interview prep? Check out **#how-it-works** to get started!")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
