from logging import Logger
from typing import List
import importlib
import argparse
import logging
import json
import os

import discord
from discord.ext import commands


class Bot(commands.Bot):
    def __init__(self) -> None:
        self._extensions: Dict[str, str] = {}
        with open("configs/main.json") as f:
            self.config = json.load(f)

        if not os.path.exists("var"):
            os.mkdir("var", 0o755)

        intents = discord.Intents.default()
        intents.message_content = True
        super(Bot, self).__init__(
            command_prefix="!",
            intents=intents
        )

    async def load_extensions(self, exts: List[str]) -> None:
        all_exts = next(os.walk("extensions/"))[1]
        for ext_name in all_exts:
            if ext_name in exts and ext_name not in self._extensions:
                cog = importlib.import_module(
                    f"extensions.{ext_name}"
                ).Cog(self)
                await self.add_cog(cog)
                self._extensions[ext_name] = cog.__cog_name__

    async def unload_extensions(self, exts: List[str]) -> None:
        for ext_name in exts:
            if ext_name in self._extensions:
                await self.remove_cog(self._extensions[ext_name])
                del self._extensions[ext_name]

    async def on_ready(self) -> None:
        logger = logging.getLogger('discord')

        await self.load_extensions(self.config["default_extensions"])
        cogs_amount = len(self._extensions)
        logger.info(f"Loaded {cogs_amount} cog{'s' if cogs_amount > 1 else ''}")

        commands = len(await self.tree.sync())
        logger.info(f"Synced {commands} command{'s' if commands > 1 else ''}")

        activity = discord.Game("shooter")
        status = discord.Status("dnd")
        await self.change_presence(activity=activity, status=status)
        logger.info("Started activity")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="NotABot",
        description="Discord bot written for Vectozavr's server",
    )
    parser.add_argument(
        'token',
        help="Token of discord bot"
    )

    args = parser.parse_args()
    bot = Bot()
    bot.run(args.token)


if __name__ == "__main__":
    main()
