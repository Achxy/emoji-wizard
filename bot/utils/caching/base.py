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

from abc import ABC, abstractmethod
from asyncio import Lock
from collections.abc import Mapping
from typing import Awaitable, ClassVar, Generator, Hashable, Iterable

from asyncpg import Pool, Record
from typing_extensions import Self

__all__: tuple[str] = ("BaseCache",)


class BaseCache(Mapping, ABC):
    __slots__: ClassVar[tuple[()]] = ()

    def __len__(self) -> int:
        return len(self.__store__)

    def __getitem__(self, key) -> Record:
        return self.__store__[key]

    def __iter__(self) -> Iterable:
        return iter(self.__store__)

    def __await__(self) -> Generator[Awaitable[None], None, Self]:
        yield from self.pull().__await__()
        return self

    async def pull(self) -> None:
        async with self.__lock__:
            resp: list[Record] = await self.pool.fetch(self.query)
            journal: dict[Hashable, Record] = {}
            for item in resp:
                journal[item[self.key]] = item

            self.__store__.clear()
            self.__store__.update(journal)

    @property
    @abstractmethod
    def pool(self) -> Pool:
        ...

    @property
    @abstractmethod
    def __lock__(self) -> Lock:
        ...

    @property
    @abstractmethod
    def __store__(self) -> dict:
        ...

    @property
    @abstractmethod
    def query(self) -> str:
        ...

    @property
    @abstractmethod
    def key(self) -> str:
        ...
