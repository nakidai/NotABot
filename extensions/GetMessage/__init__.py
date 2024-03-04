from typing import Optional
import re
from time import time

from asyncj import AsyncJson
import discord
from discord.ext import commands
from discord import app_commands


class Cog(commands.Cog, name="GetMessageCog"):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.slowestJson = AsyncJson("configs/slowest.json")

    @app_commands.command(
        name="getmsg",
        description="Get message"
    )
    @app_commands.describe(
        message_id="Message ID",
        channel_id="Channel ID (default: current channel)"
    )
    async def getmsg(
        self,
        interaction: discord.Interaction,

        message_id: str,
        channel_id: Optional[str] = None
    ) -> None:
        self.start_time = time()
        
        # Check arguments
        if not message_id.isdigit() or \
           channel_id is not None and not channel_id.isdigit():
            await interaction.response.send_message(
                "Arguments should be unsigned integers",
                ephemeral=True
            )

        _channel_id = \
            interaction.channel.id if channel_id is None else channel_id

        await self._getmsg_end(interaction, _channel_id, message_id)

    @app_commands.command(
        name="linkgetmsg",
        description="Get message by link"
    )
    @app_commands.describe(
        url="Message jump URL",
    )
    async def linkgetmsg(
        self,
        interaction: discord.Interaction,

        url: str,
    ) -> None:
        self.start_time = time()
        
        if not re.search(
            r"^https:\/\/discord.com\/channels\/(\d+)\/(\d+)\/(\d+)$",
            url
        ):
            await interaction.response.send_message(
                "Invalid link format",
                ephemeral=True
            )
            return

        url_splitted = url.split('/')
        channel_id = int(url_splitted[-2])
        message_id = int(url_splitted[-1])

        await self._getmsg_end(interaction, channel_id, message_id)

    async def _getmsg_end(
        self,
        interaction: discord.Interaction,

        channel_id: int,
        message_id: int
    ) -> None:
        # Get channel
        try:
            channel = await self.client.fetch_channel(channel_id)
        except discord.errors.NotFound:
            await interaction.response.send_message(
                "Invalid channel ID",
                ephemeral=True
            )
            return
        except discord.errors.Forbidden:
            await interaction.response.send_message(
                "I have no access to this channel",
                ephemeral=True
            )
            return

        # Get message
        try:
            message = await channel.fetch_message(message_id)
        except discord.errors.NotFound:
            await interaction.response.send_message(
                "Invalid message ID",
                ephemeral=True
            )
            return
        
        # Get timestamp
        timestamp = round(message.created_at.timestamp())

        await interaction.response.defer()

        # Get content
        content = message.content
        if not content:
            content = "Message has no text"

        # Ping protection
        content = re.sub(r"<@(\d+)>", r"user(\1)", content)
        content = re.sub(r"<@&(\d+)>", r"role(\1)", content)

        # Get files
        files = []
        try:
            for attachment in message.attachments:
                files.append(await attachment.to_file())
        except discord.HTTPException as exc:
            await interaction.response.send_message(
                "HTTPException for one of the attachments:\n{exc}",
                ephemeral=True
            )

        # Send response
        try:
            await interaction.followup.send(
                f"""
User {message.author.name} sent [message]({message.jump_url}) <t:{timestamp}:D><t:{timestamp}:T>
{content}""",
                files=files
            )
        except ValueError:
            await interaction.followup.send(
                f"""One of the files is too big, I'll not send them
User {message.author.name} sent [message]({message.jump_url}) <t:{timestamp}:D><t:{timestamp}:T>
{content}"""
            )

        self.end_time = time()
        self.elapsed_time = self.end_time - self.start_time
        
        slowestJsonData = await slowestJson.read()
        if slowestJsonData["getmessage"] > self.elapsed_time:
            slowestJsonData["getmessage"] = self.elapsed_time
            await slowestJson.write(slowestJsonData)
            await interaction.channel.send(
                f"This command took {self.elapsed_time} seconds to execute, which is the slowest execution!"
            )
