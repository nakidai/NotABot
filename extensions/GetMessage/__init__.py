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
        message_id="Message ID",
        channel_id="Channel ID (default: current channel)"
    )
    async def getmsg(
        self,
        interaction: discord.Interaction,

        message_id: str,
        channel_id: Optional[str] = None
    ) -> None:
        # Check arguments
        if not message_id.isdigit() or \
           channel_id is not None and not channel_id.isdigit():
            await interaction.response.send_message(
                "Arguments should be unsigned integers",
                ephemeral=True
            )

        # Get channel
        if channel_id is None:
            channel = interaction.channel
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
User {message.author.name} sent [message]({message.jump.url}) <t:{timestamp}:D><t:{timestamp}:T>
{content}""",
                files=files
            )
        except ValueError:
            await interaction.followup.send(
                f"""One of the files is too big, I'll not send them
User {message.author.name} sent message <t:{timestamp}:D><t:{timestamp}:T>
{content}"""
            )
