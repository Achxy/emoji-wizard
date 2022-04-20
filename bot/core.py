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
from typing import ClassVar, Coroutine, Final

from asyncpg import Pool
from discord.ext import commands
from utils.caching import PrefixCache
from utils.caching.queries import SELECT_ALL

__all__: Final[tuple[str]] = ("EmojiBot",)

logger = logging.getLogger(__name__)


class EmojiBot(commands.Bot):
    """
    The main bot class, this is a subclass of the commands.Bot
    This class is slotted and does not have a __dict__ attribute
    """

    __slots__: ClassVar[tuple[str, str]] = ("prefix", "pool")

    def __init__(self, *args, pool: Pool, **kwargs) -> None:
        if "command_prefix" in kwargs:
            raise ValueError("command_prefix need not be set manually, provide default_prefix instead")
        if (default_prefix := kwargs.pop("default_prefix")) is None:
            raise ValueError("default_prefix must be set")

        self.pool: Pool = pool
        self.prefix: PrefixCache = PrefixCache(
            default=default_prefix,
            pool=pool,
            fetch_query=SELECT_ALL,
            key="guild_id",
            pass_into=commands.when_mentioned_or,
        )
        super().__init__(*args, **kwargs, command_prefix=self.prefix)

    async def on_ready(self) -> None:
        """
        Called when the client is done preparing the data received from Discord
        Usually after login is successful and the `Client.guilds` and co. are filled up
        This can be called multiple times
        """
        logger.info("Successfully logged in as %s", self.user)

    async def setup_hook(self) -> None:
        """
        To perform asynchronous setup after the bot is logged in but
        before it has connected to the Websocket.
        Here, this will be leveraged to ready up the prefix cache
        and load extension from the `cogs` directory
        """
        # Ready up prefix
        await self.prefix
        # Load extensions
        load_ext: list[Coroutine[None, None, None]] = []
        path = (Path(__file__).parent / "cogs").resolve()

        for ext in path.glob("**/*.py"):
            load_ext.append(self.load_extension(f"cogs.{ext.stem}"))

        await asyncio.gather(*load_ext)
