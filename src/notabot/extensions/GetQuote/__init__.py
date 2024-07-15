import requests
import json

import discord
from discord.ext import commands
from discord import app_commands


class Cog(commands.Cog, name="GetQuoteCog"):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @app_commands.command(
        name="randquote",
        description="Get random quote"
    )
    async def randquote(
        self,
        interaction: discord.Interaction
    ) -> None:
        api_url = "https://api.api-ninjas.com/v1/quotes?category="
        response = requests.get(api_url, headers={'X-Api-Key': 'RYG3jNHiGlbfWOJPry9q6g==XNOxVtdu8S17eYJZ'})
        quote: dict

        if response.status_code == requests.codes.ok:
            quote = json.loads(response.text)[0]
        else:
            await interaction.response.send_message(
                "Error in sending a request to the collection of quotations",
                ephemeral=True
            )
            return
        
        text = quote["quote"]
        author = quote["author"]
        category = quote["category"]
        await interaction.response.send_message(
                f"{text}\n-# {author} - {category}",
                ephemeral=False
            )
        return
