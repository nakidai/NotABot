"""
The extension to 'NotABot' discord not a bot client, which adds '/remindme' command.
"""


import os
import json
import discord
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from discord import app_commands


# Constants
DATABASE_UPDATE_TIME: int = 5       # in seconds
PER_USER_REMINDER_LIMIT: int = 30   # how many reminders can 1 user have


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
            try:
                self.remindme_database: dict[str, list[dict[str, str]]] = json.loads(file.read())
            except json.decoder.JSONDecodeError:
                print("CRITICAL: RemindMe Unable to load the database, due to an error when decoding it")
                print("INFO: RemindMe cog is down")
                self.cog_unload()
                return

        # start checking reminders
        self.check_reminders.start()

    @app_commands.command(
        name="remindme",
        description="Reminds you"
    )
    @app_commands.describe(
        timestamp="Time after which the reminder is sent. "
                  "(Y - Year, M - month, d - day, h - hour, m - minute)",
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

        decoded_time = {
            "Y": 0,     # year
            "M": 0,     # month
            "d": 0,     # day
            "h": 0,     # hour
            "m": 0,     # minute
            # "s": 0      # second (I don't think it's needed?)
        }
        token = ""
        for char in timestamp:
            # if character is a digit
            if char.isdigit():
                token += char

            # if it's a time specifier
            elif char in "YMDhms":
                decoded_time[char] = int(token)

            # if it's a separator
            elif char == " " and token != "":
                token = ""

            # if it's garbaje~
            else:
                await interaction.response.send_message(f"Unknown character '{char}'", ephemeral=True)
                return

        # calculate the total amount of time in seconds
        total_seconds = decoded_time["Y"] * 31557600
        total_seconds += decoded_time["M"] * 2628000
        total_seconds += decoded_time["d"] * 86400
        total_seconds += decoded_time["h"] * 3600
        total_seconds += decoded_time["m"] * 60
        # total_seconds += decoded_time["s"]

        # if the total amount of time is bigger than 10 years, give an error and die
        if total_seconds > 31557600:
            await interaction.response.send_message("I doubt the discord will exist for 10+ years.", ephemeral=True)
            return

        # check if user is already present
        if (user_id := str(interaction.user.id)) in self.remindme_database:
            # if so, check if the user didn't hit the "remindme" cap
            if len(self.remindme_database[user_id]) > PER_USER_REMINDER_LIMIT:
                await interaction.response.send_message("You've reached the reminder limit of 30", ephemeral=True)
                return

        # if not, add a list for them
        else:
            self.remindme_database[user_id] = []

        # add a reminder for a user
        future_time = datetime.now()
        future_time += timedelta(0, total_seconds)
        self.remindme_database[user_id].append({
            "timestamp": future_time.strftime("%Y-%m-%d %H:%M:%S"),
            "message": message
        })

        # send the sucks ass message
        await interaction.response.send_message("Напоминание успешно создано!")

        # update the database
        self.update_remindme_database()

    @tasks.loop(seconds=DATABASE_UPDATE_TIME)
    async def check_reminders(self):
        """
        A periodic check of reminders.
        """

        # go through the database
        for user_id, reminders in self.remindme_database.items():
            # fetch the user
            user = self.client.get_user(int(user_id))

            # go through the user's reminders
            reminder_idx = 0
            while reminder_idx < len(reminders):
                # fetch the reminder
                reminder = reminders[reminder_idx]

                # decode the stored timestamp
                timestamp = datetime.strptime(reminder["timestamp"], "%Y-%m-%d %H:%M:%S")

                # if the time is negative, that means it has already past that
                if (timestamp - datetime.now()).total_seconds() <= 0:
                    message = f"Напоминание на <t:{int(timestamp.timestamp())}>\n{reminder['message']}"

                    # check that the message isn't too big
                    if len(message) >= 2000:
                        message = message[:1995] + "..."

                    # remove the reminder from the database
                    self.remindme_database[user_id].pop(reminder_idx)
                    reminder_idx -= 1

                    # try to send the reminder to the user's dm
                    try:
                        await user.send(message)

                    # if failed for these reasons, just ignore
                    except discord.HTTPException or discord.Forbidden:
                        pass

                    # if something else failed, put it in logs
                    except Exception as e:
                        print(f"WARN: {e}; in RemindMe cog")

                # increment the index
                reminder_idx += 1

        # update the database
        self.update_remindme_database()

    def update_remindme_database(self):
        """
        Updates the remindme user database
        """

        # fetch database filepath
        database = os.path.join(self.path_to_cog, "database.json")

        # check that the database file is in its place still
        # may not be necessary, but it's here anyway
        if not os.path.isfile(database):
            print("CRITICAL: RemindMe database was removed while the bot was running.")
            print("INFO: RemindMe database will be created from the one currently loaded")

        # write updates to the database file
        with open(database, "w", encoding="utf8") as file:
            file.write(json.dumps(self.remindme_database, indent=2))
