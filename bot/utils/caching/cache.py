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
from collections.abc import Mapping
from pprint import pformat
import asyncio
from typing import Awaitable, Callable, Concatenate, Generator, Iterator, Literal, ParamSpec, TypeVar
import abc
from asyncpg import Pool, Record
from typing_extensions import Self


_KT = TypeVar("_KT")
_VT = TypeVar("_VT")

P = ParamSpec("P")
R = TypeVar("R")


class BaseCache(Mapping[_KT, _VT], abc.ABC):
    """
    An abstract builder class which implements the Mapping interface
    """

    def __init__(self):
        self.__event = asyncio.Event()
        self.__event.clear()
        self.__main_cache: dict[_KT, _VT] = {}
        self.__populated: bool = False

    @staticmethod
    def raise_if_not_ready(
        func: Callable[Concatenate[BaseCache, P], R]
    ) -> Callable[Concatenate[BaseCache, P], R]:
        """
        A decorator which raises a RuntimeError if the cache is not populated yet

        Args:
            func (Callable[P, R]): The function to decorate

        Returns:
            Callable[Concatenate[BaseCache, P], R]:
                The decorated function,
                with the same signature as the original function
        """

        def wrapper(self: BaseCache, *args: P.args, **kwargs: P.kwargs) -> R:
            if not self.has_populated:
                raise RuntimeError("Cache is not populated yet")
            return func(self, *args, **kwargs)

        return wrapper

    @raise_if_not_ready
    def __str__(self) -> str:
        return pformat(self.__main_cache)

    @raise_if_not_ready
    def __getitem__(self, __k: _KT, /) -> _VT:
        return self.__main_cache[__k]

    @raise_if_not_ready
    def __len__(self) -> int:
        return len(self.__main_cache)

    @raise_if_not_ready
    def __iter__(self) -> Iterator[_KT]:
        return iter(self.__main_cache)

    def __await__(
        self,
    ) -> Generator[Awaitable[None], None, Self]:
        """
        An generator which yields a coroutine
        and then returns the same instance once finished

        Returns:
            _type_: The same instance that was awaited

        Yields:
            Generator[Awaitable[None], None, Self]:
                YieldType: Awaitable which returns None
                SendType: None
                ReturnType: The same instance that was awaited
        """
        yield from self.pull().__await__()
        return self

    async def wait_until_ready(self) -> Literal[True]:
        """
        This can be awaited to wait until the cache is ready

        Returns:
            Literal[True]: Always returns True
        """
        return await self.__event.wait()

    async def pull(self) -> None:
        """
        Pulls the data from the database and stores it in the cache
        The existing cached values (if any) is overwritten
        """
        self.__event.clear()
        response: list[Record] = await self.pool.fetch(self.fetch_query)
        journal: dict[_KT, _VT] = {}
        for val in response:
            key, val = val
            journal[key] = val
        self.__main_cache = {**journal}
        self.__event.set()
        self.__populated = True

    @property
    @abc.abstractmethod
    def fetch_query(self) -> str:
        """
        Returns the fetch query that was given to the constructor

        Returns:
            str: The fetch query
        """

    @property
    @abc.abstractmethod
    def pool(self) -> Pool:
        """
        Returns the pool that is currently in use

        Returns:
            Pool: An instance of `asyncpg.Pool`
        """

    @property
    def raw_cache(self) -> dict[_KT, _VT]:
        """
        Returns the raw cache, since this is a reference,
        changes to this dict will be reflected in the cache
        Modifying this is highly discouraged as it may tamper integrity.

        Returns:
            dict[_KT, _VT]: The raw cache
        """
        return self.__main_cache

    @property
    def has_populated(self) -> bool:
        """
        Returns whether the cache has been populated

        Returns:
            bool: Whether the cache has been populated
        """
        return self.__populated
