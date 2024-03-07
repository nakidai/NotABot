from typing import Optional

import discord
from discord.ext import commands
from discord import app_commands


class Cog(commands.Cog, name="GetAvatarCog"):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @app_commands.command(
        name="getavatar",
        description="Get message"
    )
    @app_commands.describe(
        user="User ID (default: you)",
    )
    async def getmsg(
        self,
        interaction: discord.Interaction,

        user: Optional[discord.Member] = None,
    ) -> None:
        _user = interaction.user if user is None else user

        avatar = _user.avatar
        if avatar is None:
            await interaction.response.send_message(
                "User has no avatar",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"[Avatar]({avatar.url})"
        )
