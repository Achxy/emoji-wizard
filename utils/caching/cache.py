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
    """
    An builder class which implements the Mapping interface
    Mixin methods:
        __contains__ (in)
        __eq__ (==)
        __ne__ (!=)
        keys
        values
        items
        get

    Args:
        Mapping (_type_): _description_
    """

    def __init__(self, *, fetch: str, write: str, pool: Pool):
        """
        Initialize the `BaseCache` instance.
        Provided `Pool` must be fully initialized
        before passing it into this constructor.

        Args:
            fetch (str): SQL query to fetch the data from the database
            write (str): SQL query to write the data to the database
            pool (Pool): An instance of `asyncpg.Pool`
        """
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
        """
        An generator which yields a coroutine
        and then returns the same instance once finished

        Returns:
            _type_: The same instance that was awaited

        Yields:
            Generator[Awaitable[None], None, _CT]:
                YieldType: Awaitable which returns None
                SendType: None
                ReturnType: The same instance that was awaited
        """
        yield from self.pull().__await__()
        return self

    async def pull(self) -> None:
        """
        Pulls the data from the database and stores it in the cache
        """
        response: list[Record] = await self.__pool.fetch(self.__fetch)
        journal: dict[_KT, _VT] = {}
        for val in response:
            key, val = val
            journal[key] = val
        self.__main_cache = {**journal}

    async def update(self, key: _KT, value: _VT) -> None:
        """
        Updates the value of the key in the database
        and then in the cache

        Args:
            key (_KT): The key to update
            value (_VT): The value to update
        """
        await self.__pool.execute(self.__write, key, value)
        self.__main_cache[key] = value

    @property
    def fetch_query(self) -> str:
        """
        Returns the fetch query that was given to the constructor

        Returns:
            str: The fetch query
        """
        return self.__fetch

    @property
    def write_query(self) -> str:
        """
        Returns the write query that was given to the constructor

        Returns:
            str: The write query
        """
        return self.__write

    @property
    def pool(self) -> Pool:
        """
        Returns the pool that is currently in use

        Returns:
            Pool: An instance of `asyncpg.Pool`
        """
        return self.__pool

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
