from typing import Optional

import discord
from discord.ext import commands
from discord import app_commands, Embed


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

        embed: Embed = Embed(
            title=f"Avatar {_user}",
            url=avatar.url
        )
        embed.set_image(url=avatar.url)
        await interaction.response.send_message(
            embed=embed
        )
