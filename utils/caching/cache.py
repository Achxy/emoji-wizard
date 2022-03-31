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
from collections.abc import Mapping
from pprint import pformat
from typing import Awaitable, Final, Generator, Iterator, TypeVar

from asyncpg import Pool, Record

_CT = TypeVar("_CT", bound="BaseCache")
_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


class BaseCache(Mapping[_KT, _VT]):
    def __init__(self, *, fetch: str, write: str, pool: Pool):
        self.__fetch: Final[str] = fetch
        self.__write: Final[str] = write
        self.__pool: Final[Pool] = pool
        self.default: list[str] = []
        self.__main_cache: dict[_KT, _VT] = {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__fetch}, {self.__write})"

    def __str__(self) -> str:
        return pformat(self.__main_cache)

    def __getitem__(self, __k: _KT, /) -> _VT:
        return self.__main_cache[__k]

    def __len__(self) -> int:
        return len(self.__main_cache)

    def __iter__(self) -> Iterator[_KT]:
        return iter(self.__main_cache)

    def __await__(
        self: _CT,
    ) -> Generator[Awaitable[None], None, _CT]:
        yield from self.pull().__await__()
        return self

    async def pull(self) -> None:
        response: list[Record] = await self.__pool.fetch(self.__fetch)
        journal: dict[_KT, _VT] = {}
        for val in response:
            k, v = val
            journal[k] = v
        self.__main_cache = {**journal}

    async def update(self, key: _KT, value: _VT) -> None:
        await self.__pool.execute(self.__write, key, value)
        self.__main_cache[key] = value

    @property
    def fetch_query(self) -> str:
        return self.__fetch

    @property
    def write_query(self) -> str:
        return self.__write

    @property
    def pool(self) -> Pool:
        return self.__pool

    @property
    def raw_cache(self) -> dict[_KT, _VT]:
        return self.__main_cache
