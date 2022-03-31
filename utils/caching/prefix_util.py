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

from enum import Enum
from typing import TYPE_CHECKING, Literal

from asyncpg import Pool
from discord import Message

from .cache import BaseCache

if TYPE_CHECKING:
    from ...main import EmojiBot


class _Sentinel(Enum):
    """
    Single member enum for sentinel value
    """

    MISSING = object()


class PrefixHelper(BaseCache):
    """
    A helper class for prefixes.
    This is inherited from BaseCache where the cache logic is implemented.
    """

    def __init__(
        self,
        *,
        fetch: str,
        write: str,
        pool: Pool,
        default: Literal[_Sentinel.MISSING] | list[str] = _Sentinel.MISSING,
    ):
        """
        Constructing this class is in a similar fashion to that of `BaseCache`
        however, a new keyword argument `default` is added to specify the
        default value to be expected to the cache result.

        Args:
            fetch (str): SQL query to fetch the data from the database
            write (str): SQL query to write the data to the database
            pool (Pool): An instance of `asyncpg.Pool`
            default (list[str]): A list of default prefixes to be used
        """
        self.default = default if default is not _Sentinel.MISSING else []
        super().__init__(fetch=fetch, write=write, pool=pool)

    def __call__(self, bot: EmojiBot, message: Message) -> list[str]:
        """
        This can be either passed directly into `commands.Bot` constructor
        as the `command_prefix` argument or abstracted into a another helper
        function for finer control.

        Args:
            bot (EmojiBot): An instance of `EmojiBot`
            message (Message): An instance of `discord.Message`

        Returns:
            list[str]: list of strings which are cached prefixes
        """
        ret = self.get(message.guild.id if message.guild else _Sentinel.MISSING, [])
        ret = ret if isinstance(ret, list) else [ret]

        return ret + self.default
