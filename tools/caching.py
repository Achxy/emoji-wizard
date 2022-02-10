from tools.enum_tools import TableType
import functools
import json


class Cache:
    def __init__(self, bot) -> None:
        self.bot = bot
        self._pool = bot.db
        self._ready = False

        self.caching_values = {}

    def _if_ready(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self._ready:
                raise RuntimeError("Cache is not ready")
            return func(self, *args, **kwargs)

        return wrapper

    async def populate_cache(self, *tables: TableType):
        # Tables is supposed to be an enum
        # we need to get the values of it and then pass it to the query
        # and then we can use the values to get the data from the database
        # the cache is later accessed by the same enums
        self._ready = False

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
        self._ready = True

    @_if_ready
    def get_cache(self, table: TableType):
        """
        Get the cache for a specific table
        raises RuntimeError if the cache is not ready
        """
        return self.caching_values[table.value]

    @_if_ready
    def touch(self, table: TableType, rows: list, coincide=None, increment=None):
        """
        Adds to the cache
        If coincide is True then the value will be incremented where all other row of existing row is match
            - If not matched then new row is created
        If coincide is False then then new row is created regardless.
        """
        assert isinstance(coincide, bool)
        assert isinstance(increment, int) if coincide else ...
        if not coincide:
            self.caching_values[table.value].append(rows)
            return
        # If coincide is True then the value will be incremented where all other row of existing row is match
        # - If not matched then new row is created
        # The increment value is provided seperately not within the rows
        # So it can be asserted that (rows - 1) == len(self.caching_values[table.value][0])
        # This is to prevent shooting oneself in the foot
        assert len(rows) == len(self.caching_values[table.value][0]) - 1
        # Everything is fine, we can proceed
        # increment the missing value in the row with the increment value
        for i, row in enumerate(self.caching_values[table.value]):
            if (x := set(row)) >= (y := set(rows)):
                # We got the value we are looking for, we can increment it
                inner_index = row.index(tuple(x ^ y)[0])
                self.caching_values[table.value][i][inner_index] += increment
                return

    @_if_ready
    def __str__(self) -> str:
        return json.dumps(self.caching_values, indent=4)

    @property
    def is_ready(self):
        return self._ready
