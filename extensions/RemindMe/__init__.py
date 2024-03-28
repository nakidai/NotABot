"""
The extension to 'NotABot' discord not a bot client, which adds '/remindme' command.
"""


import discord
import json
import os
import re

from datetime import datetime, timedelta
from discord.ext import commands, tasks
from discord import app_commands


# Constants
DATABASE_UPDATE_TIME: int = 5       # in seconds
PU_LIMIT: int = 30   # PER_USER_LIMIT, how many reminders can 1 user have at once


class Cog(commands.Cog, name="RemindMe"):
    """
    This is the 'remind me' command cog
    """

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

        # make sure that the database file exists
        # if an outage happens, the bot will still save the messages.
        self.db_path: str = "var/remindme_db.json"
        if not os.path.isfile(self.db_path):
            with open(self.db_path, "w", encoding="utf8") as file:
                file.write("{\n}")

        # read the database
        with open(self.db_path, "r") as file:
            try:
                self.remindme_database: dict[str, list[dict[str, str]]] = json.loads(file.read())
            except json.decoder.JSONDecodeError:
                print("WARN: RemindMe Unable to load the database, due to an error when decoding it")
                print("WARN: RemindMe cog is down")
                self.cog_unload()
                return

        # start checking reminders
        self.check_reminders.start()

    @app_commands.command(
        name="remindme",
        description="Reminds you"
    )
    @app_commands.describe(
        message="Message that needs to be reminded",
        minutes="After how many minutes send a reminder (default is 1 minute)",
        hours="After how many hours send a reminder",
        days="After how many days send a reminder",
        weeks="After how many weeks send a reminder",
        months="After how many months send a reminder",
        years="After how many years send a reminder"
    )
    async def remindme(
        self,
        interaction: discord.Interaction,

        message: str,
        minutes: int = 1,
        hours: int = 0,
        days: int = 0,
        weeks: int = 0,
        months: int = 0,
        years: int = 0
    ) -> None:
        """
        This is the 'remind me' command implementation
        """

        # timedelta
        timed = timedelta(
            minutes=minutes,
            hours=hours,
            days=days + (months * 30.436875) + (years * 365.2422),
            weeks=weeks
        )

        # make a pretty error embed
        error_embed = discord.Embed(title="Error!", description="You've got an error", color=discord.Color.red())

        # if the total amount of time is bigger than 10 years, give an error and die
        if timed.days > 3652:
            # add a field to an error embed
            error_embed.add_field(name="Message", value="I doubt the discord will exist for 10+ years.",
                                  inline=False)

            # send the error message
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        # check if user is already present
        if (user_id := str(interaction.user.id)) in self.remindme_database:
            # if so, check if the user didn't hit the "remindme" cap
            if len(self.remindme_database[user_id]) > PU_LIMIT:
                # add a field to an error embed
                error_embed.add_field(name="Message", value=f"You've reached the reminder limit of {PU_LIMIT}",
                                      inline=False)

                # send the error message
                await interaction.response.send_message(embed=error_embed, ephemeral=True)
                return

        # if not, add a list for them
        else:
            self.remindme_database[user_id] = []

        # filter pings from message
        message = re.sub(r"<@(\d+)>", r"user(\1)", message)
        message = re.sub(r"<@&(\d+)>", r"role(\1)", message)

        # add a reminder for a user
        future_time = datetime.now() + timed
        self.remindme_database[user_id].append({
            "timestamp": future_time.strftime("%Y-%m-%d %H:%M:%S"),
            "message": message
        })

        # make a pretty embed
        embed = discord.Embed(title="Success!", description="Reminder successfully created!",
                              color=discord.Color.green())
        embed.add_field(name="You will receive a message on", value=f"<t:{int(future_time.timestamp())}>",
                        inline=False)

        # send the success message
        await interaction.response.send_message(embed=embed, ephemeral=True)

        # update the database
        self.update_remindme_database()

    @tasks.loop(seconds=DATABASE_UPDATE_TIME)
    async def check_reminders(self):
        """
        A periodic check of reminders.
        """

        # go through the database
        for user_id, reminders in self.remindme_database.items():
            # go through the user's reminders
            reminder_idx = 0
            while reminder_idx < len(reminders):
                # fetch the reminder
                reminder = reminders[reminder_idx]

                # decode the stored timestamp
                timestamp = datetime.strptime(reminder["timestamp"], "%Y-%m-%d %H:%M:%S")

                # if the time is negative, that means it has already past that
                if (timestamp - datetime.now()).total_seconds() <= 0:
                    # get user class
                    username = self.client.get_user(int(user_id))

                    # generate a message
                    message = (f"Reminder for <t:{int(timestamp.timestamp())}> for {username.mention}\n"
                               f"{reminder['message']}")

                    # check that the message isn't too big
                    if len(message) >= 2000:
                        message = message[:1990] + "..."

                    # make a pretty embed if possible
                    if len(message) < 100:
                        embed = discord.Embed(title="Reminder!", description="Your reminder")
                        embed.add_field(name="Message", value=reminder['message'], inline=False)
                    else:
                        embed = None

                    # remove the reminder from the database
                    self.remindme_database[user_id].pop(reminder_idx)
                    reminder_idx -= 1

                    # try to fetch channel
                    try:
                        channel = await self.client.fetch_channel(
                            int(reminder['channel'])
                        )

                    # if failed for these reasons, just ignore
                    except discord.HTTPException or discord.Forbidden:
                        pass

                    # if something else failed, put it in logs
                    except Exception as e:
                        print(f"WARN: {e}; in RemindMe cog")

                    # try to send the reminder
                    try:
                        if embed is None:
                            await channel.send(message)
                        else:
                            await channel.send(embed=embed)

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

        # check that the database file is in its place still
        # may not be necessary, but it's here anyway
        if not os.path.isfile(self.db_path):
            print("WARN: RemindMe database was removed while the bot was running.")
            print("INFO: RemindMe database will be created from the one currently loaded")

        # write updates to the database file
        with open(self.db_path, "w", encoding="utf8") as file:
            file.write(json.dumps(self.remindme_database, indent=2))
