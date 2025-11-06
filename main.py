"""
TODO:
2. Providing questions from Neetcode 150 (2 questions each with link and name of the problem)
3. and assigning random roles (Interviewer or Candidate)
"""

import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import logging
from dotenv import load_dotenv
from neetcode_list import NEETCODE_LIST
import os

load_dotenv()
# Railway sets this automatically in production
IS_PRODUCTION = os.getenv('RAILWAY_ENVIRONMENT') is not None
if IS_PRODUCTION:
    token = os.getenv('DISCORD_TOKEN')
    ALLOWED_CHANNEL = 1433269455500087297
    INTERVIEW_ROOM_CATEGORY_ID = 1433270003419058279
    print("🚀 Running in PRODUCTION mode (Railway)")
else:
    token = os.getenv('TESTING_BOT_CODE')
    ALLOWED_CHANNEL = 1436017919418175489
    INTERVIEW_ROOM_CATEGORY_ID = 1436017919418175492
    print("🧪 Running in DEVELOPMENT mode (Local)")

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

    if interaction.channel.id != ALLOWED_CHANNEL:
        await interaction.response.send_message(
            f"Please use this command in #find-partner!",
            ephemeral=True
        )
        return

    for queue_name, queue_list in queue.items():
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
            f"✅ You've successfully joined the **{chosen_name}** interview queue!\n"
            f"👥 Currently {len(queue[diff])} participants waiting.\n"
            f"Once matched, a private interview text + voice channel will be created for you!",
            ephemeral=True
        )
    else:
        display_name = difficulty.name
        queue[diff].append(user)
        await interaction.response.send_message(
            f"🎲 Random difficulty chosen: **{display_name}**\n"
            f"✅ You've successfully joined the **{display_name}** interview queue!\n"
            f"👥 Currently {len(queue[diff])} participants waiting.\n"
            f"Once matched, a private interview text + voice channel will be created for you!",
            ephemeral=True
        )
    await try_match(interaction.guild, diff)


# Drop the queue command: /leave-queue
@bot.tree.command(name="leave-queue", description="Leave the interview queue")
async def leave_queue(interaction: discord.Interaction):
    user = interaction.user

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

        text_channel = await guild.create_text_channel(
            name=f"interview-{difficulty}",
            category=category,
            overwrites=overwrite,
            reason=f"Mock interview text channel for {user1.name} and {user2.name}"
        )
        interview_channel = await guild.create_voice_channel(
            name=f"mock interview - {difficulty}",
            category=category,
            overwrites=overwrite,
            reason=f"mock interview room for {user1.name} and {user2.name}"
        )
        # Problems from neetcode dict
        problems = random.sample(NEETCODE_LIST[difficulty], 2)

        # Randomly assigning roles
        roles = random.sample([user1, user2], 2)
        interviewer_first = roles[0]
        candidate_first = roles[1]

        message = f"""\
        🎯 **Mock Interview - {difficulty.capitalize()}**
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        👥 **Participants:**
        {interviewer_first.mention}
        {candidate_first.mention}
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        📝 **Round 1**
        **Interviewer:** {interviewer_first.mention}  
        **Candidate:** {candidate_first.mention}  
        **Problem:** [{problems[0]['name']}]({problems[0]['link']})
        
        📝 **Round 2**
        **Interviewer:** {candidate_first.mention}  
        **Candidate:** {interviewer_first.mention}  
        **Problem:** [{problems[1]['name']}]({problems[1]['link']})
        
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        💡 **Guidelines:**
        Interviewers: Only look at **your** problem  
        Suggested time: 30–45 minutes per round  
        Switch roles after Round 1  
        
        🎙️ **Voice Channel:** {interview_channel.mention}
        """.strip()

        await text_channel.send(message)

        print(f"The {interview_channel} was created")
        # Commented it out to test if it's better to just have a temp text channel or have the bot DM personally
        '''
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
        '''

        # Store in active interviews for tracking
        interview_id = f"{user1.id}_{user2.id}"
        active_interviews[interview_id] = {
            'channel': interview_channel,
            'text': text_channel,
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


async def end_interview_room(interview_id):
    try:
        if interview_id in active_interviews:
            data = active_interviews[interview_id]

            voice_channel = data['channel']
            text_channel = data['text']

            await voice_channel.delete(reason=f"Interview Ended - a participant left")
            print(f"the voice channel was deleted successfully: {voice_channel.name}")

            await text_channel.delete(reason=f"Interview Ended - a participant left")
            print(f"the text channel was deleted successfully: {text_channel.name}")

    except Exception as e:
        print(f"Error deleting interview room: {e}")


@bot.event
# Detect when interview participants leave and end the interview
async def on_voice_state_update(member, before, after):
    # member = the user who had a voice state change
    # before = their voice state BEFORE the change
    # after = their voice state AFTER the change
    if before.channel and (not after.channel or before.channel.id != after.channel.id):
        channel = before.channel

        if channel.name.startswith("mock interview"):
            print(f"{member.name} left the channel {member.name}")

            for interview_id, data in list(active_interviews.items()):
                if data['channel'].id == channel.id and member in data['users']:  #NOTE (member condition is redudant)
                    print(f"Participant {member.name} has left the interview - waiting 25 seconds")
                    await asyncio.sleep(25)  # A small grace period if someone disconnects

                    try:
                        if member not in channel.members:
                            print(f"{member.name} did not rejoin within 25s — ending interview.")
                            await end_interview_room(interview_id)

                            difficulty = data['difficulty']
                            remaining_user = next((u for u in data['users'] if u != member), None)

                            if remaining_user:
                                # Disconnect the remaining user if still connected
                                if remaining_user.voice and remaining_user.voice.channel:
                                    try:
                                        await remaining_user.move_to(None)
                                        print(
                                            f"{remaining_user.name} has been removed from the voice channel after partner left.")
                                    except discord.Forbidden:
                                        print(f"Cannot disconnect {remaining_user.name} — missing permissions.")

                                # Send an interactive DM using inline view and buttons
                                try:
                                    view = discord.ui.View(timeout=30)

                                    # ✅ Yes Button
                                    async def yes_callback(interaction: discord.Interaction):
                                        queue[difficulty].append(remaining_user)
                                        await interaction.response.edit_message(
                                            content=f"✅ You’ve been requeued in the **{difficulty.capitalize()}** queue!",
                                            view=None
                                        )
                                        print(f"{remaining_user.name} rejoined the {difficulty} queue.")
                                        await try_match(channel.guild, difficulty)

                                    # ❌ No Button
                                    async def no_callback(interaction: discord.Interaction):
                                        await interaction.response.edit_message(
                                            content="👌 No problem — you’ve not been requeued.",
                                            view=None
                                        )
                                        print(f"{remaining_user.name} chose not to rejoin the queue.")

                                    # Add both buttons to the View
                                    yes_button = discord.ui.Button(label="✅ Yes, rejoin",
                                                                   style=discord.ButtonStyle.success)
                                    no_button = discord.ui.Button(label="❌ No, thanks",
                                                                  style=discord.ButtonStyle.danger)

                                    yes_button.callback = yes_callback
                                    no_button.callback = no_callback

                                    view.add_item(yes_button)
                                    view.add_item(no_button)

                                    await remaining_user.send(
                                        f"😔 Your interview partner **{member.name}** left the session and the room has been closed.\n\n"
                                        f"Would you like to **rejoin the {difficulty.capitalize()} queue** to find a new partner?",
                                        view=view
                                    )

                                except discord.Forbidden:
                                    print(f"Could not DM {remaining_user.name}, DMs disabled.")

                            # Clean up from active_interviews
                            del active_interviews[interview_id]

                    except discord.NotFound:
                        print("This channel is long gone")
                    break


@bot.event
async def on_member_join(member):
    await member.send(
        f"🎯 Welcome, {member.name}! Ready to level up your interview prep? Check out **#how-it-works** to get started!")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
