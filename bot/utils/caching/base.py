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

import logging
from abc import ABC, abstractmethod
from asyncio import Lock
from collections.abc import Mapping
from pprint import pformat
from typing import Awaitable, ClassVar, Generator, Hashable, Iterable

from asyncpg import Pool, Record
from typing_extensions import Self

__all__: tuple[str] = ("BaseCache",)

logger = logging.getLogger(__name__)


class BaseCache(Mapping, ABC):
    """
    BaseCache is a builder class for caching asyncpg records.
    This implements `collections.abc.Mapping`

    Abstract methods (or properties) are:
        query (property)
        key (property)
        pool (property)
        __store__ (property)
        __lock__ (property)
    Mixins methods:
        __str__
        pull

    """

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

    def __str__(self) -> str:
        return pformat(self.__store__)

    async def pull(self) -> None:
        """
        Pulls all the values from the database and stores them in the __store__
        mapping, the key is the value of the key property.
        """
        async with self.__lock__:
            clsname = self.__class__.__name__
            logger.info("Pulling data for %s", clsname)
            resp: list[Record] = await self.pool.fetch(self.query)
            logger.debug("Pulled data for %s: %s", clsname, resp)
            journal: dict[Hashable, list[Record]] = {}

            for item in resp:
                journal.setdefault(item[self.key], []).append(item)

            self.__store__.clear()
            self.__store__.update({**journal})
            logger.info(
                "Completed pulling data for %s, held %s records in memory (%s in store)",
                clsname,
                len(resp),
                len(self.__store__),
            )

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
