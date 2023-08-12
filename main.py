import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# command to subscribe (role optional)
def run():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!@#",
                       intents=intents, help_command=None)

    @bot.event
    async def on_ready():
        print(f"User: {bot.user} (ID: {bot.user.id})")
        # sync global commands
        bot.sync = await bot.tree.sync()
        print(f'synced {len(bot.sync)} commands')

    bot.run(token)


if __name__ == "__main__":
    run()
