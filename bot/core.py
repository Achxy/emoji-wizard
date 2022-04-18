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
import logging
from pathlib import Path
from typing import Coroutine, Final, Iterable

from asyncpg import Pool
from discord import Message
from discord.ext import commands
from utils.caching import PrefixCache
from utils.caching.queries import SELECT_ALL

__all__: Final[tuple[str]] = ("EmojiBot",)

logger = logging.getLogger(__name__)


def get_prefix(target_bot: EmojiBot, message: Message) -> Iterable[str]:
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
    return target_bot.prefix(target_bot, message)


class EmojiBot(commands.Bot):
    """
    The main bot class, this is a subclass of the commands.Bot
    This class is slotted and does not have a __dict__ attribute
    """

    __slots__: tuple[str, str] = ("prefix", "pool")

    def __init__(self, *args, pool: Pool, **kwargs) -> None:
        if "command_prefix" in kwargs:
            raise ValueError("command_prefix need not be set manually, provide default_prefix instead")
        if (default_prefix := kwargs.pop("default_prefix", None)) is None:
            raise ValueError("default_prefix must be set")

        self.pool: Pool = pool
        self.prefix: PrefixCache = PrefixCache(
            default=default_prefix,
            pool=pool,
            fetch_query=SELECT_ALL,
            key="guild_id",
            pass_into=commands.when_mentioned_or,
            mix_with_default=True,
        )
        super().__init__(*args, **kwargs, command_prefix=get_prefix)

    async def on_ready(self) -> None:
        """
        Called when the client is done preparing the data received from Discord
        Usually after login is successful and the `Client.guilds` and co. are filled up
        This can be called multiple times
        """
        logger.info("Successfully logged in as %s", self.user)

    async def setup_hook(self) -> None:
        load_ext: list[Coroutine[None, None, None]] = []
        path = (Path(__file__).parent / "cogs").resolve()

        for ext in path.glob("**/*.py"):
            load_ext.append(self.load_extension(f"cogs.{ext.stem}"))

        await asyncio.gather(*load_ext)
