from typing import Optional

import discord
from discord.ext import commands
from discord import app_commands

from .field import Field


class Cog(commands.Cog, name="MinesweeperCog"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(
        name="ms-gen",
        description="Generates minesweeper field")
    @app_commands.describe(
        size="Size of the field ((0, 10)) (default: 9)",
        mines="Number of mines on the field ((0, size^2]) (default: 10)")
    async def ms_gen(
        self,
        interaction: discord.Interaction,

        size: Optional[int] = 9,
        mines: Optional[int] = 10
    ) -> None:
        if size >= 10 or size <= 0 or mines <= 0 or mines > size**2:
            await interaction.response.send_message(
                "Incorrect values",
                ephemeral=True
            )
            return
        field = Field(size, mines)
        field.generate()
        await interaction.response.send_message(f"Minesweeper\n{field}")
