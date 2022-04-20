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

from asyncio import Lock
from itertools import repeat
from typing import Awaitable, ClassVar, Final, Generator, Hashable, Iterable

from asyncpg import Pool, Record
from typeshack import PassIntoBase
from typing_extensions import Self

from .base import BaseCache
from .queries import CREATE_PREFIX_TABLE, INSERT, REMOVE, REMOVE_ALL, SELECT

__all__: Final[tuple[str]] = ("PrefixCache",)


class PrefixCache(BaseCache):
    """
    Caches the prefixes for every guild available in the database.
    """

    __slots__: ClassVar[tuple[str, ...]] = (
        "__pool",
        "__fetch_query",
        "__key",
        "default",
        "pass_into",
        "__lock",
        "__store",
    )

    def __init__(
        self,
        *,
        pool: Pool,
        fetch_query: str,
        key: str,
        default: Iterable[str],
        pass_into: PassIntoBase = lambda *pfx: lambda bot, message: pfx,
        lock: Lock | None = None,
    ) -> None:
        self.__pool: Pool = pool
        self.__fetch_query: str = fetch_query
        self.__key: str = key
        self.default: Iterable[str] = default
        self.pass_into: PassIntoBase = pass_into
        self.__lock: Lock = lock or Lock()
        self.__store: dict[Hashable, Record] = {}

    def __await__(self) -> Generator[Awaitable[None], None, Self]:
        yield from self.ensure_table_exists().__await__()
        yield from self.pull().__await__()
        return self

    def __call__(self, bot, message) -> Iterable[str]:
        ret: list[Record] = self[message.guild.id]
        if ret is None:
            return self.pass_into(*self.default)(bot, message)
        return self.pass_into(*self.default, *ret)(bot, message)

    async def pull_for(self, guild_id: int) -> None:
        """
        Similar to `pull`, but only pulls for the specified guild.
        This is useful for when you want to pull for a specific guild, rather
        than populating the entire cache.

        Args:
            guild_id (int): The guild ID to pull for.
        """
        async with self.__lock__:
            resp: list[Record] = await self.pool.fetch(SELECT, guild_id)
            self.__store[guild_id] = resp

    async def ensure_table_exists(self) -> None:
        """
        Execute the table create query on the pool
        This should create the table if it doesn't exist already
        This function is yielded when a instance of this class is awaited
        """
        async with self.__lock__:
            await self.pool.execute(CREATE_PREFIX_TABLE)

    async def append(self, guild_id: int, prefix: str) -> None:
        """
        Adds a prefix to the database and the cache.

        Args:
            guild_id (int): The guild ID to add the prefix to
            prefix (str): The prefix to add
        """
        async with self.__lock__:
            await self.pool.execute(INSERT, guild_id, prefix)

    async def extend(self, guild_id: int, prefixes: Iterable[str]) -> None:
        """
        Adds multiple prefixes to the database and the cache.

        Args:
            guild_id (int): The guild ID to add the prefixes to
            prefixes (Iterable[str]): An iterable of prefixes to add
        """
        async with self.__lock__:
            await self.pool.executemany(INSERT, (repeat(guild_id), prefixes))

    async def remove(self, guild_id: int, prefix: str) -> None:
        """
        Removes a prefix from the database and the cache.

        Args:
            guild_id (int): The guild ID to remove the prefix from
            prefix (str): The prefix itself to be removed
        """
        async with self.__lock__:
            await self.pool.execute(REMOVE, guild_id, prefix)

    async def clear(self, guild_id: int) -> None:
        """
        Clears all the prefixes for a given guild.

        Args:
            guild_id (int): The guild ID to clear the record from
        """
        async with self.__lock__:
            await self.pool.execute(REMOVE_ALL, guild_id)

    @property
    def pool(self) -> Pool:
        return self.__pool

    @property
    def __store__(self) -> dict:
        return self.__store

    @property
    def __lock__(self) -> Lock:
        return self.__lock

    @property
    def query(self) -> str:
        return self.__fetch_query

    @property
    def key(self) -> str:
        return self.__key
