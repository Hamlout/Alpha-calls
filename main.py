import os
import json

import discord
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
    # if file does not exist
    data = {}
    if not os.path.exists("data.json"):
        with open("data.json", 'w') as f:
            json.dump(data, f, indent=4)
    
    # if file exist
    with open("data.json", 'r') as f:
        data = json.load(f)
        
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
        # Check for role if provided or not
        if role:
            status = f"{role.mention} will be pinged"
            role = role.id
        else:
            status = "no role will be pinged"

        data = reading_from_json()

        try: # update info if guild has entry in json file
            del data[str(interaction.guild_id)]
            await update_subscription(data, interaction, role, status)
        except KeyError: # add info if guild has no entry in json file
            await update_subscription(data, interaction, role, status)
    
    @bot.tree.command(name="unsubscribe", description="stop sharing calls in current channel")
    async def unsubscribe(interaction: discord.Interaction):

        data = reading_from_json()

        try:  # delete guild entry in json file
            del data[str(interaction.guild_id)]
            with open("data.json", 'w') as f:
                json.dump(data, f, indent=4)
            await interaction.response.send_message(f"This channel will stop posting calls", ephemeral=True)
        except KeyError:  # if guild is not subscribed. nothing to delete
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
        max_length=1000,
        placeholder="Message content"
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Generating the call", ephemeral=True)
        with open("data.json", 'r') as f:
            data = json.load(f)
        for server in data:  # loop over all the servers added
            # get the objects
            channel_id = data[server]['channel']
            role_id = data[server]['role']
            guild = interaction.client.get_guild(int(server))
            if guild:
                role = guild.get_role(role_id)
                channel = guild.get_channel(channel_id)
                # generating the embed
                embed = discord.Embed(title=self.fb_title.value,
                                    description=self.message.value,
                                    color=discord.Color.yellow()
                                    )
                embed.set_image(url=self.image)
                embed.set_footer(text=self.user.nick)
                content = ""
                if role: # check if role is added to ping
                    content = f"{role.mention}"
                try:
                    await channel.send(content=content, embed=embed)
                except discord.errors.Forbidden:
                    await channel.send(f"Make sure the bot has the correct permissions", ephemeral=True)

if __name__ == "__main__":
    run()
