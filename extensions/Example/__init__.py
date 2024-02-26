"""
This is extension, which stores cog. In folder with this file you can place any
code you want related to this cog (btw I recommend you place one command per
cog if it's complicated, or group several small commands by one theme).

Root of the bot has folder configs, where you should place configs for your
extension. This way it would be easy to edit bot configuration. You should name
it by name of the extension in lower case or create folder of extension name if
you need several configs.
"""

import json

import discord
from discord.ext import commands
from discord import app_commands


class Cog(commands.Cog, name="ExampleCog"):
    """
    This is cog, where you can register some commands.

    Cog should be subclass of discord.ext.commands.Cog, should be names as Cog,
    and you should give it unique name (because Cog sounds not very unique).
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        In __init__ you should set self.client to first argument (there it's
        called as client) and also there you can load some configs, set some
        default variables etc.

        In this example it loads welcome message from the config file.
        """
        with open("configs/example.json") as f:
            self.greeting = json.load(f)["greeting"]
        self.client = client

    @app_commands.command(
        name="hello",
        description="Say hello"
    )
    @app_commands.describe(
        name="Your name (default: \"Vectozavr\")"
    )
    async def hello(
        self,
        interaction: discord.Interaction,

        name: str = "Vectozavr"
    ) -> None:
        """
        This is command. You should name command short and informative. Also
        it's nice to add description, especially if you command is complicated.
        I don't know what does method name, so you can name it as you want, but
        make its name related to the command name.

        If you have arguments, it's nice to add description to them so user can
        see what does each argument.

        In this example it sends message with greetings and name from name
        arguments or uses "Vectozavr" if argument not provided.
        """

        # Protection from pings
        _name = name.replace("@", "%40%")
        await interaction.response.send_message(f"{self.greeting}, {_name}!")
