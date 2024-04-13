from typing import Optional

import discord
from discord.ext import commands
from discord import app_commands, Embed

from ...utils import Color


class Cog(commands.Cog, name="GetAvatarCog"):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @app_commands.command(
        name="getavatar",
        description="Get user's avatar"
    )
    @app_commands.describe(
        user="User ID (default: you)",
    )
    async def getmsg(
        self,
        interaction: discord.Interaction,

        user: Optional[discord.Member] = None
    ) -> None:
        _user = interaction.user if user is None else user

        avatar = (await self.client.fetch_user(_user.id)).avatar
        if avatar is None:
            await interaction.response.send_message(
                f"{_user.name} has no avatar",
                ephemeral=True
            )
            return

        embed: Embed = Embed(
            title=f"{_user.name}'s avatar",
            url=avatar.url,
            color=Color.EMBED_BACKGROUND_DARK
        )
        embed.set_image(url=avatar.url)
        await interaction.response.send_message(
            embed=embed
        )

    @app_commands.command(
        name="getbanner",
        description="Get user's banner"
    )
    @app_commands.describe(
        user="User ID (default: you)"
    )
    async def getbanner(
        self,
        interaction: discord.Interaction,

        user: Optional[discord.Member] = None
    ) -> None:
        _user = interaction.user if user is None else user

        banner = (await self.client.fetch_user(_user.id)).banner
        if banner is None:
            await interaction.response.send_message(
                f"{_user.name} has no banner",
                ephemeral=True
            )
            return

        embed: Embed = Embed(
            title=f"{_user.name}'s banner",
            url=banner.url,
            color=Color.EMBED_BACKGROUND_DARK
        )
        embed.set_image(url=banner.url)
        await interaction.response.send_message(
            embed=embed
        )
