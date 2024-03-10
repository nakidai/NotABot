"""
The extension to 'NotABot' discord not a bot client, which adds '!remindme' command.
"""

import os
import json
import discord
from datetime import datetime
from discord.ext import commands
from discord import app_commands


class Cog(commands.Cog, name="RemindMe"):
    """
    This is the 'remind me' command cog
    """

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

        # make sure that the database file exists
        # if an outage happens, the bot will still save the messages.
        self.path_to_cog: str = os.path.abspath(os.path.dirname(__file__))
        filepath = os.path.join(self.path_to_cog, "database.json")
        if not os.path.isfile(filepath):
            with open(filepath, "w", encoding="utf8") as file:
                file.write("{\n}")

        # read the database
        with open(filepath, "r") as file:
            self.remindme_database: dict[str, list[dict[str, str]]] = json.loads(file.read())

    @app_commands.command(
        name="remindme",
        description="Reminds you"
    )
    @app_commands.describe(
        timestamp="Time after which the reminder is sent. "
                  "(Y - Year, M - month, d - day, h - hour, m - minute, s - second)",
        message="Message that needs to be reminded"
    )
    async def remindme(
        self,
        interaction: discord.Interaction,

        timestamp: str,
        message: str
    ) -> None:
        """
        This is the 'remind me' command implementation
        """

        time = timestamp
        decoded_time = {
            "Y": 0,     # year
            "M": 0,     # month
            "d": 0,     # day
            "h": 0,     # hour
            "m": 0,     # minute
            # "s": 0      # second (I don't think it's needed?)
        }
        token = ""
        for char in time:
            if char.isdigit():
                token += char
            elif char in "YMDhms":
                try:
                    decoded_time[char] = int(token)
                except ValueError:
                    raise discord.ext.commands.BadArgument
            elif char == " " and token != "":
                token = ""

        # calculate the total amount of time in years
        total_years = decoded_time["Y"]
        total_years += decoded_time["M"] / 12
        total_years += decoded_time["d"] / 365.2422
        total_years += decoded_time["h"] / 8766
        total_years += decoded_time["m"] / 525960
        # total_years += decoded_time["s"] / 31557600  # to lessen the load

        # if the total amount of time is bigger than 10 years, give an error and die
        if total_years > 10:
            await interaction.response.send_message("Я не думаю что Discord будет существовать через 10 лет.")
            return

        # check if user is already present
        if (user_id := str(interaction.user.id)) in self.remindme_database:
            # if so, check if the user didn't hit the "remindme" cap
            if len(self.remindme_database[user_id]) > 30:
                await interaction.response.send_message("Вы достигли лимита напоминаний в 30")
                return
        else:
            self.remindme_database[user_id] = []

        # add a reminder for a user
        self.remindme_database[user_id].append({
            "timestamp": datetime.now().__str__(),
            "message": message
        })

        await interaction.response.send_message("Напоминание успешно создано!")
