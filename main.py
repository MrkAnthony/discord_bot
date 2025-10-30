'''
TODO:
Add a check so that people who are already in queue cannot join another queue unless they leave
Add the logic for matching into a room with problem
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
        await interaction.response.send_message(
            f"🎲 Random difficulty chosen: **{chosen_name}**\n"
            f"✅ You've joined the **{chosen_name}** queue!\n"
            f"👥 Currently {len(queue[diff])} people waiting.\n"
            f"You'll be notified when matched!",
            ephemeral=True
        )
    else:
        display_name = difficulty.name
        await interaction.response.send_message(
            f"You've joined the **{display_name}** queue!\n"
            f"👥 Currently {len(queue[diff])} people waiting.\n"
            f"You'll be notified when matched!",
            ephemeral=True
        )

    queue[diff].append(user)
    await try_match(interaction.guild, diff)


# Drop the queue command: /leave-queue
@bot.tree.command(name="leave-queue", description="Leave the interview queue")
async def leave_queue(interaction: discord.Interaction):
    user = interaction.user

    ALLOWED_CHANNEL = 1433269455500087297

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
    INTERVIEW_ROOM_CATEGORY_ID = 1433269372255731874
    category = guild.get_channel(INTERVIEW_ROOM_CATEGORY_ID)

    if not category:
        print("This wasn't found")

    overwrite = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),  # Hide from everyone
        user1: discord.PermissionOverwrite(view_channel=True, connect=True),   # Allow user1
        user2: discord.PermissionOverwrite(view_channel=True, connect=True),   # Allow user2
        guild.me: discord.PermissionOverwrite(view_channel=True, connect=True, move_members=True)  # Bot permissions
    }

@bot.event
async def on_member_join(member):
    await member.send(
        f"🎯 Welcome, {member.name}! Ready to level up your interview prep? Check out **#how-it-works** to get started!")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
