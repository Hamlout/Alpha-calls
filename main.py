import os
import json

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

async def update_subscription(data, interaction, role, status):
    data.update({interaction.guild_id: {"channel": interaction.channel_id, "role": role}})
    with open("data.json", 'w') as f:
        json.dump(data, f, indent=4)
    await interaction.response.send_message(f"This channel will start posting and {status}", ephemeral=True)

def reading_from_json():
    try:  # if file exist
        with open("data.json", 'r') as f:
            data = json.load(f)
    except FileNotFoundError: # if file does not exist
        data = {}
        with open("data.json", 'w') as f:
            json.dump(data, f, indent=4)
    return data

def run():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!@#",
                       intents=intents, help_command=None)

    @bot.event
    async def on_ready():
        print(f"User: {bot.user} (ID: {bot.user.id})")
        bot.sync = await bot.tree.sync()
        print(f'synced {len(bot.sync)} commands')

    @bot.tree.command(name="subscribe", description="Share calls in current channel")
    async def subscribe(interaction: discord.Interaction, role: discord.Role = None):
        # Check for role if provided
        if role:
            status = f"{role.mention} will be pinged"
            role = role.id
        else:
            status = "no role will be pinged"

        data = reading_from_json()

        try: # if guild is subscribed, delete the old info then update the new ones
            del data[str(interaction.guild_id)]
            await update_subscription(data, interaction, role, status)
        except KeyError: # if guild is not subscribed, just update the new info
            await update_subscription(data, interaction, role, status)
    
    @bot.tree.command(name="unsubscribe", description="stop sharing calls in current channel")
    async def unsubscribe(interaction: discord.Interaction):

        data = reading_from_json()

        try:
            del data[str(interaction.guild_id)]
            with open("data.json", 'w') as f:
                json.dump(data, f, indent=4)
            await interaction.response.send_message(f"This channel will stop posting calls", ephemeral=True)
        except KeyError:
            await interaction.response.send_message(f"This guild is not subscribed", ephemeral=True)

    @bot.tree.command(name="call", description="Make call")
    async def call(interaction: discord.Interaction, file: discord.Attachment = None):
        feedback_modal = FeedbackModal()
        feedback_modal.user = interaction.user
        feedback_modal.image = None
        if file:
            feedback_modal.image = file
        await interaction.response.send_modal(feedback_modal)

    bot.run(token)

class FeedbackModal(discord.ui.Modal, title="Send us your feedback"):
    fb_title = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Title",
        required=False,
        placeholder="Give your feedback a title"
    )

    message = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="Message",
        required=True,
        max_length=500,
        placeholder="Message content"
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(973631848712372324)
        embed = discord.Embed(title=self.fb_title.value,
                              description=self.message.value,
                              color=discord.Color.yellow()
                              )
        print(self.image)
        embed.set_image(url=self.image)
        embed.set_footer(text=self.user.nick)
        try:
            await channel.send(embed=embed)
            await interaction.response.send_message(f"Thank you, {self.user.nick}", ephemeral=True)
        except discord.errors.Forbidden:
            await interaction.response.send_message(f"Make sure the bot has the correct permissions", ephemeral=True)

if __name__ == "__main__":
    run()
