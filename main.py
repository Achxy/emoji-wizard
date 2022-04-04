"""
EmojiWizard is a project licensed under GNU Affero General Public License.
Copyright (C) 2022-present  Achxy

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from __future__ import annotations

import asyncio
from typing import Final

import asyncpg
from discord import Intents, Message
from discord.ext import commands

from tools import findenv
from utils import PrefixHelper

DEFAULT_PREFIX: Final[list[str]] = ["?"]


def get_prefix(target_bot: EmojiBot, message: Message) -> list[str]:
    """
    The callable which can be passed into commands.Bot
    constructor as the command_prefix kwarg.

    Internally this gets the `prefix` attribute of the the bot
    which is a `PrefixHelper` instance.

    Args:
        target_bot (EmojiBot): commands.Bot instance or subclass instance
        message (Message): discord.Message object.

    Returns:
        list[str]: The prefixes for the guild, along with the defaults
    """
    return target_bot.prefix(bot, message)


class EmojiBot(commands.Bot):
    """
    The main bot class, this is a subclass of the commands.Bot
    This class is slotted and does not have a __dict__ attribute
    """

    __slots__: tuple[str, str] = ("prefix", "pool")

    async def on_ready(self) -> None:
        """
        Called when the client is done preparing the data received from Discord
        Usually after login is successful and the `Client.guilds` and co. are filled up
        This can be called multiple times
        """
        print(f"Successfully logged in as {self.user}")


async def main(target_bot: EmojiBot) -> None:
    """
    The main function assignes values to some of bot's slotted attributes
    And starts the bot

    Args:
        target_bot (EmojiBot): an instance of `EmojiBot`
    """
    async with target_bot:
        target_bot.pool = await asyncpg.create_pool(dsn=findenv("DATABASE_URL"))
        target_bot.prefix = await PrefixHelper(
            fetch="SELECT * FROM prefixes",
            write="INSERT INTO prefixes VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET prefix = $2",
            pool=target_bot.pool,
            default=DEFAULT_PREFIX,
            pass_into=commands.when_mentioned_or,
        )
        print(target_bot.prefix)
        await target_bot.start(findenv("DISCORD_TOKEN"))


bot: EmojiBot = EmojiBot(command_prefix=get_prefix, intents=Intents.all())


@bot.command()
async def prefix(ctx):
    return await ctx.send(bot.prefix[ctx.guild.id])


if __name__ == "__main__":
    asyncio.run(main(bot))
