from collections.abc import Mapping
from pprint import pformat
from typing import Awaitable, Generator, Iterator, TypeVar

from asyncpg import Pool, Record

_CT = TypeVar("_CT", bound="BaseCache")
_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


class BaseCache(Mapping[_KT, _VT]):
    def __init__(self, *, fetch: str, write: str, pool: Pool):
        self.fetch: str = fetch
        self.write: str = write
        self.pool: Pool = pool
        self.default: list[str] = []
        self.main_cache: dict[_KT, _VT] = {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.fetch}, {self.write})"

    def __str__(self) -> str:
        return pformat(self.main_cache)

    def __getitem__(self, __k: _KT, /) -> _VT:
        return self.main_cache[__k]

    def __len__(self) -> int:
        return len(self.main_cache)

    def __iter__(self) -> Iterator[_KT]:
        return iter(self.main_cache)

    def __await__(
        self: _CT,
    ) -> Generator[Awaitable[None], None, _CT]:
        yield from self.pull().__await__()
        return self

    async def pull(self) -> None:
        response: list[Record] = await self.pool.fetch(self.fetch)
        journal: dict[_KT, _VT] = {}
        for val in response:
            k, v = val
            journal[k] = v
        self.main_cache = {**journal}

    async def update(self, key: _KT, value: _VT) -> None:
        await self.pool.execute(self.write, key, value)
        self.main_cache[key] = value
