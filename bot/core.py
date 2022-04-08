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

from typing import Final, Iterable

from asyncpg import Pool
from discord import Message
from discord.ext import commands

__all__: Final[tuple[str]] = ("EmojiBot",)

MISSING = object()


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
    return target_bot.prefix(target_bot, message)


class EmojiBot(commands.Bot):
    """
    The main bot class, this is a subclass of the commands.Bot
    This class is slotted and does not have a __dict__ attribute
    """

    __slots__: tuple[str, str] = ("prefix", "pool")

    def __init__(self, *args, pool: Pool, default_prefix: Iterable[str], **kwargs) -> None:
        if kwargs.get("command_prefix", MISSING) is not MISSING:
            raise ValueError(
                (
                    "manually providing command_prefix is not necessary "
                    "you should only provide default_prefix and have prefixes cached automatically"
                    "from the database"
                )
            )
        self.pool: Pool = pool
        super().__init__(*args, **kwargs)

    async def on_ready(self) -> None:
        """
        Called when the client is done preparing the data received from Discord
        Usually after login is successful and the `Client.guilds` and co. are filled up
        This can be called multiple times
        """
        print(f"Successfully logged in as {self.user}")
