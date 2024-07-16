import requests
import json

import discord
from discord.ext import commands
from discord import app_commands


class Cog(commands.Cog, name="GetQuoteCog"):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.qapikey = ""

    @app_commands.command(
        name="randquote",
        description="Get random quote"
    )
    async def randquote(
        self,
        interaction: discord.Interaction
    ) -> None:
        if self.qapikey == "":
            await interaction.response.send_message(
                "Use /setqapikey to set quote APi key, please.\nGet API key - https://api-ninjas.com/api/quotes",
                ephemeral=True
            )
            return
        api_url = "https://api.api-ninjas.com/v1/quotes?category="
        response = requests.get(api_url, headers={"X-Api-Key": self.qapikey})
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
    
    @app_commands.command(
        name="setqapikey",
        description="Set quote API key"
    )
    @app_commands.describe(
        key="Key"
    )
    async def setqapikey(
        self,
        interaction: discord.Interaction,
        key: str
    ) -> None:
        self.qapikey = key
        await interaction.response.send_message(
                "Key applied",
                ephemeral=True
            )
        return