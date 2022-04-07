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
from pprint import pformat
from typing import Awaitable, Final, Generator, Iterable, Literal

from asyncpg import Pool
from discord import Message
from typing_extensions import Self

from .cache import BaseCache
from .typeshack import EmojiBot, PassIntoBase


class _Sentinel(Enum):
    """
    Single member enum for sentinel value
    """

    MISSING: Final = object()


class PrefixHelper(BaseCache[int, list[str]]):
    """
    A helper class for prefixes.
    This is inherited from BaseCache where the cache logic is implemented.
    """

    __slots__: tuple[str, str] = ("default", "pass_into")

    def __init__(
        self,
        *,
        fetch: str,
        write: str,
        pool: Pool,
        default: Literal[_Sentinel.MISSING] | Iterable[str] = _Sentinel.MISSING,
        pass_into: PassIntoBase = lambda *x: lambda bot, msg: list(x),
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
            pass_into:
                A function which takes in a varadic of prefixes (str) and returns a function
                which takes in an instance of `EmojiBot` and an instance of `discord.Message`
                and returns a list of prefixes.
                This is primarily targeted for use with `commands.when_mentioned_or`
        """
        self.default: tuple[str, ...] = tuple(default) if default is not _Sentinel.MISSING else ()
        self.pass_into: PassIntoBase = pass_into
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
        if message.guild is None:
            return self.pass_into(*self.default)(bot, message)

        ret: list[str] = self.get(message.guild.id, [])
        ret = ret if isinstance(ret, list) else [ret]

        return self.pass_into(*self.default, *ret)(bot, message)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}(fetch={self.fetch_query}, write={self.write_query}, "
            f"pool={self.pool!r}), default={self.default!r}, pass_into={self.pass_into!r}>"
        )

    def __str__(self) -> str:
        default = self.default
        return pformat(self.raw_cache) + f"\n{default = }"

    async def ensure_table_exists(self) -> None:
        """
        Calling this executes the SQL query to create the table for storing
        prefixes if it does not exist already in the database.
        """
        query: str = """
                CREATE TABLE IF NOT EXISTS prefixes (
                    guild_id bigint NOT NULL,
                    prefix text NOT NULL,
                    CONSTRAINT prefixes_pkey PRIMARY KEY (guild_id)
                );
                """
        await self.pool.execute(query)

    def __await__(self) -> Generator[Awaitable[None], None, Self]:
        yield from self.ensure_table_exists().__await__()
        yield from self.pull().__await__()
        return self
