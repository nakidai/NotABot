import discord
from discord.ext import commands
from discord import app_commands

class Cog(commands.Cog, name="TestCog"):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @app_commands.command(
        name="getmsg",
        description="Get message by link"
    )
    @app_commands.describe(
        link="Link on message"
    )
    async def getmsg(
        self,
        interaction: discord.Interaction,

        link: str
    ) -> None:
        await interaction.response.send_message("Message")
