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
    def touch(
        self, table: TableType, rows: list, coincide=None, increment_or_new_value=None
    ):
        """
        Adds to the cache
        If coincide is True then the value will be incremented where all other row of existing row is match
            - If not matched then new row is created
        If coincide is False then then new row is created regardless.
        """
        assert isinstance(coincide, bool)
        assert isinstance(increment_or_new_value, int) if coincide else ...
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
                self.caching_values[table.value][i][
                    inner_index
                ] += increment_or_new_value
                return

    @_if_ready
    async def get_prefix(self, table, guild_id, default_prefix):
        """
        This function can actually write to the database
        returns the custom prefix of the guild if available in cache
        else writes the default to database and returns it
        """
        if guild_id not in self.caching_values[table.value]:
            query = f"INSERT INTO {table.value} VALUES ($1, $2)"
            await self._pool.execute(query, guild_id, default_prefix)
            return default_prefix
        # Return the prefix in the cache
        for i in self.caching_values[table.value]:
            if i[0] == guild_id:
                return i[1]

    @_if_ready
    def __str__(self) -> str:
        return json.dumps(self.caching_values, indent=4)

    @property
    def is_ready(self):
        return self._ready
