from __future__ import annotations

import asyncio
import functools
from .mixins import NonDunderMutableMappingMixin
from collections.abc import Awaitable, Callable
from pprint import pformat
from typing import Concatenate, Final, Generator, Iterable, Literal, TypeVar

from asyncpg import Pool

from .events import EventDispatchers
from .hints import (
    CPT,
    AsyncDestination,
    AsyncOuterDecoratorHint,
    P,
    R,
    SyncOuterDecoratorHint,
)

__all__ = ("CachingPod",)

MISSING: Final[object] = object()
_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


class CachingPod(NonDunderMutableMappingMixin[_KT, _VT], EventDispatchers):

    __slots__: tuple[str, ...] = (
        "__pool",
        "__main_cache",
        "__key",
        "__value",
        "__table",
        "__create",
        "__insert",
        "__update",
        "__delete",
        "__ensure_key_is_primary",
        "__dispatch_destinations",
        "__wait",
        "__has_started",
        "__is_ready",
    )

    def __init__(
        self,
        *,
        table: str,
        key: str,
        value: str,
        create: str,
        insert: str,
        update: str,
        delete: str,
        pool: Pool | None = None,
        ensure_key_is_primary: bool = True,
    ) -> None:
        """
        Initialize the CachingPod, this can be used with a CachingPod for more control
        or can be used as a stand alone application

        Args:
            table (str): The table in the database to of which to cache
            key (str): The key name used get cached data
            value (str): The value that should be stored
            insert (str): Query that should be used to insert a new value
            update (str): Query that should be used to update an existing value
            delete (str): Query that should be used to delete an existing value
            pool (Pool | None, optional): A asyncpg.Pool that depicts a connection to the database
                                          This not being provided will render most of the methods
                                          of the CachingPod unusable.
                                          Pool is not required to be provided if used in CachingCluster
            ensure_key_is_primary (bool, optional): Raises error if the provided key is not primary key
                                                    in the provided table. Defaults to True.
        Warning:
        !   All queries are assumed to trusted and sanitized
        !   Queries are NOT sanitized internally
        """
        # Pool will be finalized if it's not None
        self.__pool: Pool | None = pool
        self.__main_cache: dict[_KT, _VT] = {}
        self.__key: Final[str] = key
        self.__value: Final[str] = value
        self.__table: Final[str] = table
        # TODO: Implement `insert` and `update` and `delete`
        self.__create: Final[str] = create
        self.__insert: Final[str] = insert
        self.__update: Final[str] = update
        self.__delete: Final[str] = delete
        self.__ensure_key_is_primary: Final[bool] = ensure_key_is_primary
        self.__dispatch_destinations: AsyncDestination = {}
        self.__wait: Final[asyncio.Event] = asyncio.Event()
        self.__has_started: bool = False
        self.__is_ready: bool = False

    @property
    def __destinations__(self) -> AsyncDestination:
        """
        A property which returns the destinations
        This is not the part of Public API
        This overrides the abstract property of EventDispatchers

        Returns:
            AsyncDestination: dict with str key containing list of async functions
        """
        return self.__dispatch_destinations

    @staticmethod
    def _event_lock(
        wait_for_previous: bool = True, set_on_fail: bool = True
    ) -> AsyncOuterDecoratorHint:
        def decorator(
            func: Callable[Concatenate[CPT, P], Awaitable[R]]
        ) -> Callable[Concatenate[CPT, P], Awaitable[R]]:
            @functools.wraps(func)
            async def wrapper(self: CPT, *args: P.args, **kwargs: P.kwargs) -> R:
                if (
                    not self.__wait.is_set()
                    and wait_for_previous
                    and self.__has_started
                ):
                    # We need to make sure that the previous task is done or if it doesn't exist
                    # Because we start off not being ready, as such we mustn't wait for the previous
                    # In such cases, (which'll never set) and we forever wait
                    # This is why __has_started is important
                    # The alternative is to starting off ready which is a bad idea because it will cause
                    # false dispatches
                    await self.__wait.wait()
                self.__wait.clear()
                self.__has_started = True
                try:
                    ret = await func(self, *args, **kwargs)
                    self.__wait.set()
                    return ret
                except Exception as e:
                    if set_on_fail:
                        self.__wait.set()
                    raise e

            return wrapper

        return decorator

    @staticmethod
    def _checkup(
        check_event: bool = False,
        check_pull_done: bool = True,
        check_pool: bool = True,
    ) -> SyncOuterDecoratorHint:
        def innner(
            func: Callable[Concatenate[CPT, P], R]
        ) -> Callable[Concatenate[CPT, P], R]:
            @functools.wraps(func)
            def wrapper(self: CPT, *args: P.args, **kwargs: P.kwargs) -> R:
                if check_event and not self.__wait.is_set():
                    raise RuntimeError("asyncio.Event has not resolved to being set")
                if check_pull_done and not self.__is_ready:
                    raise RuntimeError(
                        "CachingPod has not been able to get data (wasn't pulled) but tried to access it"
                    )
                if check_pool and self.__pool is None:
                    raise RuntimeError(
                        "CachingPod has no Pool, use activate(pool) to set it"
                    )

                return func(self, *args, **kwargs)

            return wrapper

        return innner

    @_checkup(check_pool=True, check_pull_done=False)
    async def wait_until_ready(self) -> Awaitable[Literal[True]]:
        """
        An awaitable that will block until the CachingPod is ready to be used
        This internally is Asyncio.Event.wait() where the event is set when the CachingPod is ready

        Returns:
            Awaitable[Literal[True]]: Expression will evaluate to True once the CachingPod is ready
        """
        return self.__wait.wait()

    @_event_lock()
    @_checkup(check_pull_done=False, check_pool=True)
    async def pull(self) -> None:
        """
        Pulls the data from the database and stores it in the cache

        Returns:
            None
        Preconditions:
            Pool is present
        Raises:
            ConnectionError: A connection pool is not present
            ValueError: If the key is administered as a primary key but isn't a primary key

        """
        if self.__pool is None:  # Pool is never None if we're here (see _checkup)
            # This is to satisfy static linters
            raise ConnectionError("No database connection")

        if self.__ensure_key_is_primary:
            query = """
                    SELECT
                        column_name as PRIMARYKEYCOLUMN

                    FROM
                        INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS TC

                    INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS KU
                        ON TC.CONSTRAINT_TYPE = 'PRIMARY KEY'
                        AND TC.CONSTRAINT_NAME = KU.CONSTRAINT_NAME
                        AND KU.table_name= $1

                    ORDER BY
                        KU.TABLE_NAME,
                        KU.ORDINAL_POSITION;
                    """
            primaries: list[str] = list(
                map(
                    lambda x: x["primarykeycolumn"],
                    await self.__pool.fetch(query, self.__table),
                )
            )

            if self.__key not in primaries:
                raise ValueError(f"{self.__key} is not a primary key")

        query = f"SELECT {self.__key}, {self.__value} FROM {self.__table}"
        journal: dict[_KT, _VT] = {}
        for row in await self.__pool.fetch(query):
            journal[row[self.__key]] = row[self.__value]
        self.__main_cache = {**journal}  # Deep copy
        del journal
        self.__is_ready = True
        # __is_ready isn't fully representative of whether the cache is ready
        # much rather than internal check to see if the pull has been done
        # for user-serviceable is_ready, see the `is_ready` property
        await self._dispatch("on_pull", None)

    @_checkup(check_pull_done=True)
    def get(self, key: _KT, default: R = None) -> _VT | R:
        """
        Gets a value from the cache.
        unlike the __getitem__ method, this method will not raise an error if the key is not found
        and instead will return the default value
        this is similar to the behavior of the dict.get method

        Args:
            key (_KT): The key to get the value from
            default (R, optional): The value to return instead if key is not found. Defaults to None.

        Returns:
            _VT | R: The value associated with the key or the default value if the key is not found
        Preconditions:
            Pull is done
        """
        if key in self.__main_cache:
            return self.__main_cache[key]
        return default

    async def activate(self, pool: Pool | Awaitable[Pool]) -> None:
        """
        To assign a connection pool to the caching pod
        only if a connection pool isn't only present

        Args:
            pool: The connection pool to assign to the caching pod

        Returns:
            None

        Raises:
            RuntimeError: A connection is already present
            TypeError: Provided pool isn't an instance of asyncpg.Pool,
                       Awaiting didn't resolve to an instance of asyncpg.Pool
                       or the provided object isn't awaitable at all

        Example:
            >>> async def main():
            >>>     pool = await asyncpg.create_pool(...)
            >>>     cache = CachingPod(...) # pool is not set
            >>>     await cache.activate(pool) # pool is now set

        An sort of important dev note:
            An asyncio.Pool object is awaitable by behaviour
            But we also want to accept awaitables which return Pool

            using the await syntax internally calls __await__
            Pool's __await__ calls _async__init__
            This, well, initializes the pool
            but the interesting part is that it immediately calls returns None
            if the pool is already initialized (ie, if _initilized is True)
            so we won't waste time on the awaitable if it's already been done

            It gets interesting, however
            if all the conditions are met and the pool is not initialized
            then we get an instance of the Pool (after _initilize is executed internally in Pool)
            This is extremely ideal and good because it prevents alot of unnecessary checks
            and initializes the pool if not already done

            Tracing back of such an case would look like this:
                __await__ returns the _async__init__ coroutine
                _async__init__ returns None if the pool is already initialized
                else it returns the pool instance
        """

        if self.__pool is not None:
            raise RuntimeError("Pool has already been set")

        invalid_type_exc: TypeError = TypeError(
            (
                "pool must be an instance asyncpg.Pool "
                "or a awaitable which returns "
                f"an instance of asyncpg.Pool, got {type(pool)}"
            )
        )

        try:
            resultant_pool: Pool | None = await pool
        except TypeError as active_type_exc:
            raise invalid_type_exc from active_type_exc

        if isinstance(resultant_pool, Pool):
            self.__pool = resultant_pool
            await self._dispatch("on_activate", resultant_pool)
            return

        if resultant_pool is not None:
            # It is a awaitable which neither returns a Pool nor None
            raise TypeError(
                f"Expected awaitable to return type 'Pool' got {type(resultant_pool)}"
            )

        if not isinstance(pool, Pool):
            # Not a Pool and not a awaitable
            raise invalid_type_exc

        self.__pool = pool
        await self._dispatch("on_activate", pool)

    @_checkup(check_pull_done=True)
    def __iter__(self) -> Iterable[_KT]:
        """
        An iterable of keys in the cache

        Returns:
            Iterable[_KT]: Iterable of keys present in the cache
        Preconditions:
            Pull is done
        """
        return iter(self.__main_cache)

    @_checkup(check_pull_done=True)
    def __len__(self) -> int:
        """
        Returns the number of key-value pairs in the cache

        Returns:
            int: number depicting the number of key-value pairs in the cache
        Preconditions:
            Pull is done
        """
        return len(self.__main_cache)

    @_checkup(check_pull_done=False, check_pool=True)
    def __await__(self: CPT) -> Generator[Awaitable[None], None, CPT]:
        """
        await instance to complete `pull` and return itself

        Returns:
            CachingPod: Same instance that was awaited

        Preconditions:
            Pool is present

        Yields:
            Generator[Awaitable[None], None, CachingPod]:
                YieldType: Awaitable that completes `pull`
                SendType: None
                ReturnType: CachingPod
        """
        yield from self.pull().__await__()
        return self

    @_checkup(check_pull_done=True)
    def __str__(self) -> str:
        """
        Returns a string representation of the cache
        This calls the __str__ method of the underlying cache
        roughly equivalent to:
            >>> str(self.__main_cache)
        The return string is reformatted using `pprint.pformat`

        Returns:
            str: String representation of the cache (pretty formatted)
        Preconditions:
            Pull is done
        """
        return pformat(self.__main_cache)

    @property
    def pool(self) -> Pool | None:
        """
        Returns the connection pool associated with the caching pod
        that is currently active, this is None if no pool is active

        Returns:
            Optional Pool: The connection pool associated with the caching pod
        """
        return self.__pool

    @property
    @_checkup(check_pull_done=True)
    def raw_cache(self) -> dict[_KT, _VT]:
        """
        Returns the raw cache that is being used
        Though this is a property with no setter,
        the return is a reference than a deep copy of the cache

        Returns:
            dict[_KT, _VT]: The raw cache
        Preconditions:
            Pull is done
        """
        return self.__main_cache

    @property
    def key(self) -> str:
        """
        Returns the key column name

        Returns:
            str: key name
        """
        return self.__key

    @property
    def value(self) -> str:
        """
        Returns the value column name

        Returns:
            str: column name
        """
        return self.__value

    @property
    def table(self) -> str:
        """
        Returns the table name associated with the cache

        Returns:
            str: Table name
        """
        return self.__table

    @property
    def is_ready(self) -> bool:
        """
        Property to check if the cache is ready to be used
        Value of this property may change during runtime

        Returns:
            bool: True if the cache is ready to be used
                  False otherwise
        """
        return self.__is_ready and self.__has_started and self.__wait.is_set()
