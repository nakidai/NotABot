from typing import List
import importlib
import argparse
import json
import os

import discord
from discord.ext import commands


class Bot(commands.Bot):
    def __init__(self) -> None:
        self._cogs: Dict[str, str] = {}
        with open("configs/main.json") as f:
            self.config = json.load(f)
        super(Bot, self).__init__(
            command_prefix="!",
            intents=discord.Intents.all()
        )
    
    async def load_cogs(self, cogs: List[str]) -> None:
        _cogs = __import__("cogs")

        all_cogs = next(os.walk("cogs/"))[1]
        for cog_name in all_cogs:
            if cog_name in cogs and cog_name not in self._cogs:
                cog = importlib.import_module(f"cogs.{cog_name}").Cog(self)
                await self.add_cog(cog)
                self._cogs[cog_name] = cog.__cog_name__

    async def unload_cogs(self, cogs: List[str]) -> None:
        for cog_name in cogs:
            if cog_name in self._cogs:
                await self.remove_cog(self._cogs[cog_name])
                del self._cogs[cog_name]

    async def on_ready(self) -> None:
        # TODO: Use a logger there instead of prints
        await self.load_cogs(self.config["default_cogs"])
        cogs_amount = len(self._cogs)
        print(f"Loaded {cogs_amount} cog{'s' if cogs_amount > 1 else ''}")

        commands = len(await self.tree.sync())
        print(f"Synced {commands} command{'s' if commands > 1 else ''}")

        activity = discord.Game("shooter")
        status = discord.Status("dnd")
        await self.change_presence(activity=activity, status=status)


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
