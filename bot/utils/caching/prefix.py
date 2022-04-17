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
from enum import Enum
from itertools import repeat
from typing import Awaitable, Final, Generator, Iterable

from asyncpg import Pool
from typing_extensions import Self

from .base import BaseCache
from .queries import CREATE_PREFIX_TABLE, INSERT, REMOVE, REMOVE_ALL  # pylint: disable=no-name-in-module

# TODO: Why is pylint complaining about the import?

__all__: Final[tuple[str]] = ("PrefixCache",)


class _Sentinel(Enum):
    MISSING = object()


class PrefixCache(BaseCache):
    def __init__(
        self, *, pool, fetch_query, key, default, pass_into, lock=None, mix_with_default=True
    ) -> None:
        self.__pool = pool
        self.__fetch_query = fetch_query
        self.__key = key
        self.default = default
        self.pass_into = pass_into
        self.__lock = lock or Lock()
        self.mix_with_default = mix_with_default
        self.__store = {}

    def __await__(self) -> Generator[Awaitable[None], None, Self]:
        yield from self.ensure_table_exists().__await__()
        yield from self.pull().__await__()
        return self

    def __call__(self, bot, message) -> Iterable[str]:
        ret = self.__store.get(message.guild.id, _Sentinel.MISSING)

        if ret is _Sentinel.MISSING:
            return self.default
        if self.mix_with_default:
            return self.pass_into(*ret, *self.default)
        return self.pass_into(*ret)

    async def ensure_table_exists(self) -> None:
        async with self.__lock__:
            await self.pool.execute(CREATE_PREFIX_TABLE)

    async def append(self, guild_id: int, prefix: str) -> None:
        async with self.__lock__:
            await self.pool.execute(INSERT, guild_id, prefix)

    async def extend(self, guild_id: int, prefixes: Iterable[str]) -> None:
        async with self.__lock__:
            await self.pool.executemany(INSERT, (repeat(guild_id), prefixes))

    async def remove(self, guild_id: int, prefix: str) -> None:
        async with self.__lock__:
            await self.pool.execute(REMOVE, guild_id, prefix)

    async def clear(self, guild_id: int) -> None:
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
