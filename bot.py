import os
import discord
from discord.ext import commands, tasks
from random import randrange
from dotenv import dotenv_values

config = {
    **dotenv_values(".env"),
    **os.environ,
}

# Load the bot token from the environment
TOKEN: str = config.get("BOT_TOKEN")

# Define the bot with the necessary intents
intents = discord.Intents.default()
intents.messages = True

# Create a bot instance
bot = commands.Bot(command_prefix="/", intents=intents)

# Background task to update the bot's activity
@tasks.loop(minutes=10)
async def update_activity():
    activity_texts = [
        f"In {len(bot.guilds)} servers!",
    ]

    index: int = randrange(len(activity_texts))
    text: str = activity_texts[index]
    activity = discord.CustomActivity(name=text)
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"Updating Discord Presence: {text}")


async def load_extensions():
    await bot.load_extension("commands.Greetings")
    await bot.load_extension("commands.Conversions")

# Sync slash commands on bot startup
@bot.event
async def on_ready():
    try:
        await load_extensions()

        await bot.tree.sync()  # Sync commands to Discord
        print(f"Logged in as {bot.user}! Slash commands synced.")

        update_activity.start()  # Start the activity updater task
    except Exception as e:
        print(f"Failed to start bot: {e}")


if __name__ == "__main__":
    bot.run(TOKEN)
