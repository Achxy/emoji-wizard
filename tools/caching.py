import functools
import json
import asyncio
from tools.enum_tools import TableType
from enum import Enum
from tools.bot_tools import get_default_prefix


DEFAULT_PREFIX: str = get_default_prefix()


class InterpolateAction(Enum):
    overwrite = 1
    coincide = 2
    append = 3
    destruct = 4


class Cache:
    def __init__(self, bot) -> None:
        self.bot = bot
        self._pool = bot.db
        self._ready = True
        self._event = asyncio.Event()
        asyncio.create_task(self.wait_until_ready(self._event))
        self._event.set()

        self.caching_values = {}

    async def wait_until_ready(self, event):
        self._ready = False
        await event.wait()
        self._ready = True

    def _if_ready(func):
        """
        Decorator to check if the cache is ready before executing the function
        Wait for the cache to be ready before executing the function
        Lock the cache while executing the function
        This decorator ALWAYS returns a coroutine (even if the function is not)
        """

        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not self._ready:
                # Some other function is occupying.
                # Wait for the cache to be ready
                print("Waiting for cache to be ready")
                await self.wait_until_ready(self._event)
                # Lock the cache
                self._event.clear()
                if asyncio.iscoroutinefunction(func):
                    r = await func(self, *args, **kwargs)
                else:
                    r = func(self, *args, **kwargs)
                # Unlock the cache
                self._event.set()
                return r
            # Cache is already ready
            # Occuply it for ourselves
            print("Occupying cache")
            self._event.clear()
            if asyncio.iscoroutinefunction(func):
                r = await func(self, *args, **kwargs)
            else:
                r = func(self, *args, **kwargs)
            # Unlock the cache
            self._event.set()
            return r

        return wrapper

    @_if_ready
    async def populate_cache(self, *tables: TableType):
        # Tables is supposed to be an enum
        # we need to get the values of it and then pass it to the query
        # and then we can use the values to get the data from the database
        # the cache is later accessed by the same enums

        # Clear the existing cache
        self.caching_values.clear()

        for tb in map(lambda x: x.value, tables):
            query = f"SELECT * FROM {tb}"
            data = await self._pool.fetch(query)
            # Since this part was a success,
            # We can delete the previous cache
            if tb in self.caching_values:
                del self.caching_values[tb]

            self.caching_values[tb] = [
                [v for v in n] for n in [j.values() for j in data]
            ]

    @_if_ready
    def get_cache(self, table: TableType):
        """
        Get the cache for a specific table
        raises RuntimeError if the cache is not ready
        """
        return self.caching_values[table.value]

    @_if_ready
    def interpolate(
        self, table: TableType, rows: list, action: InterpolateAction = None, value=None
    ):
        """
        Adds to the cache
        If coincide is True then the value will be incremented where all other row of existing row is match
            - If not matched then new row is created
        If coincide is False then then new row is created regardless.
        """
        assert (
            (isinstance(value, int) and isinstance(action, InterpolateAction))
            or (action is InterpolateAction.append and value is None)
            or (action is InterpolateAction.destruct and value is None)
        )

        if action is InterpolateAction.destruct:
            self.caching_values[table.value] = [
                n for n in self.caching_values[table.value] if not n == rows
            ]
            return

        if action is InterpolateAction.append:
            self.caching_values[table.value].append(rows)
            return

        # Everything is fine, we can proceed
        # take action upon the non-provided row
        for i, row in enumerate(self.caching_values[table.value]):
            if (x := set(row)) >= (y := set(rows)):
                # We got the value we are looking for, we can act upon it
                inner_index = row.index(tuple(x ^ y)[0])
                if action is InterpolateAction.overwrite:
                    self.caching_values[table.value][i][inner_index] = value
                    return
                self.caching_values[table.value][i][inner_index] += value  # Is coincide
                return

    @_if_ready
    async def get_prefix(self, table, guild_id, default_prefix=DEFAULT_PREFIX):
        """
        This function can actually write to the database
        returns the custom prefix of the guild if available in cache
        else writes the default to database and returns it
        """
        # In cache and db, the row's first value should represent the guild_id
        if guild_id not in map(lambda d: d[0], self.caching_values[table.value]):
            query = f"INSERT INTO {table.value} VALUES ($1, $2)"
            await self._pool.execute(query, guild_id, default_prefix)
            return default_prefix
        # Return the prefix in the cache
        for i in self.caching_values[table.value]:
            if i[0] == guild_id:
                return i[1]

    @_if_ready
    def print_cache(self):
        v = json.dumps(self.caching_values, indent=4)
        print(v)
        return v

    @property
    def is_ready(self):
        """
        Returns True if the cache is ready
        This value may change several times during the runtime
        """
        return self._ready
