import json

import requests
import discord
from discord.ext import commands
from discord import app_commands


class Cog(commands.Cog, name="TopicCog"):
    request_url = "https://tools.originality.ai/tool-title-generator\
/title-generator-backend/generate.php"

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @app_commands.command(
        name="topic",
        description="Current topic"
    )
    async def topic(
        self,
        interaction: discord.Interaction,
    ) -> None:
        await interaction.response.defer()

        request = ""
        async for message in interaction.channel.history(limit=100):
            if len(request) + len(message.content) >= 4097:
                break
            request = message.content + '\n' + request

        response = requests.post(Cog.request_url, data=request)
        if response.status_code != 200:
            await interaction.followup.send(
                "Cannot get topic"
            )
            return

        response = json.loads(response.url.text.split('\n')[-1])
        response = re.sub(r"<@(\d+)>", r"user(\1)", response)
        response = re.sub(r"<@&(\d+)>", r"role(\1)", response)
        await interaction.followup.send(
            "Current topic: {response}"
        )
