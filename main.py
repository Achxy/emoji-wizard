from __future__ import annotations

import asyncio
import os
from typing import Final

import asyncpg
from discord import Intents, Message
from discord.ext import commands

from utils import PrefixHelper


def get_prefix(_bot: EmojiBot, message: Message) -> list[str]:
    """
    The callable which can be passed into commands.Bot
    constructor as the command_prefix kwarg.

    Internally this gets the `prefix` attribute of the the bot
    which is a `PrefixHelper` instance.

    Args:
        _bot (EmojiBot): commands.Bot instance or subclass instance
        message (Message): discord.Message object.

    Returns:
        list[str]: The prefixes for the guild, along with the defaults
    """
    return _bot.prefix(bot, message)


class EmojiBot(commands.Bot):
    __slots__: tuple[str, str] = ("prefix", "pool")

    async def on_ready(self) -> None:
        print(f"Successfully logged in as {self.user}")


async def main(_bot) -> None:
    async with _bot:
        _bot.pool = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
        _bot.prefix = await PrefixHelper(
            fetch="SELECT * FROM prefixes",
            write="INSERT INTO prefixes VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET prefix = $2",
            pool=_bot.pool,
        )
        print(_bot.prefix)
        await _bot.start(os.getenv("DISCORD_TOKEN"))


bot: Final[EmojiBot] = EmojiBot(command_prefix=get_prefix, intents=Intents.all())


@bot.command()
async def prefix(ctx):
    return await ctx.send(bot.prefix[ctx.guild.id])


if __name__ == "__main__":
    asyncio.run(main(bot))
