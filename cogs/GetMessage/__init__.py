from typing import Optional
import re

import discord
from discord.ext import commands
from discord import app_commands


class Cog(commands.Cog, name="GetMessageCog"):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @app_commands.command(
        name="getmsg",
        description="Get message"
    )
    @app_commands.describe(
        message_id="Message ID"
        channel_id="Channel ID (default: current channel)"
    )
    async def hello(
        self,
        interaction: discord.Interaction,

        message_id: int
        channel_id: Optional[int] = None
    ) -> None:

        # Get channel
        if channel_id is None:
            channel = ineraction.channel
        else:
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
            message = channel
        except discord.errors.NotFound:
            await interaction.response.send_message(
                "Invalid message ID",
                ephemeral=True
            )
            return

        # Get timestamp
        timestamp = round(message.created_at.timestamp())

        # Get content
        content = message.content
        if not content:
            content = "Message has no text"

        # Ping protection
        content = re.sub(r"<@(\d+)>", r"user(\1)", content)
        content = re.sub(r"<@&(\d+)>", r"role(\1)", content)

        # Get files
        files = []
        async with interaction.channel.typing():
            try:
                for attachment in msg.attachments:
                    files.append(await attachment.to_file())
            except discord.HTTPException as exc:
                await interaction.response.send_message(
                    "HTTPException for one of the attachments:\n{exc}",
                    ephemeral=True
                )

        try:
            await interaction.response.send_message(
                f"""
User {msg.author.name} sent message <t:{timestamp}:D><t:{timestamp}:T>
{content}""",
                files=files
            )
        except ValueError:
            await interaction.response.send_message(
                f"""One of the files is too big, I'll not send them
User {msg.author.name} sent message <t:{timestamp}:D><t:{timestamp}:T>
{content}"""
            )
