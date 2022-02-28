from __future__ import annotations

import asyncpg as _asyncpg
import sqlite3 as _sqlite3

import time as _time
import re as _re
from .queries import Queries as _Queries
from string import Template as _Template
from asyncpg import connection as _connection, protocol as _protocol, Record as _Record
from typing import Any, Iterator, Iterable, Union


__all__: tuple[str, str] = (
    "LiteCache",
    "create_caching_pool",
)


class LiteCache(_asyncpg.Pool):
    """
    The inherited class from asyncpg.Pool
    the args that __init__ takes are similar to that of parent's __init__

    When the instance of the class is awaited, tables from the remote psql
    database are pulled into the in-memory sqlite database.
    Important: schema respect is public, this project didn't need that feature.
    This can however be extended by making table name precede with `column_record.schema_name`
    and making appropriate changes in `self.pull`

    TODO: There are more methods that can be implemented / overwritten
    """

    def __init__(
        self,
        dsn=None,
        *,
        min_size=10,
        max_size=10,
        max_queries=50000,
        max_inactive_connection_lifetime=300.0,
        setup=None,
        init=None,
        loop=None,
        connection_class=_connection.Connection,
        record_class=_protocol.Record,
        **connect_kwargs,
    ) -> None:

        super().__init__(
            dsn=dsn,
            connection_class=connection_class,
            record_class=record_class,
            min_size=min_size,
            max_size=max_size,
            max_queries=max_queries,
            loop=loop,
            setup=setup,
            init=init,
            max_inactive_connection_lifetime=max_inactive_connection_lifetime,
            **connect_kwargs,
        )

        self._lite_con = _sqlite3.connect(":memory:")
        self._cursor = self._lite_con.cursor()

    async def pull(self) -> None:
        """
        Casts the remote database into local sqlite database
        If the table is already present in the local cache, prexisting data is overwritten
        """
        print("Collecting tables...")
        # Start the timer to see how long this takes
        t_start = _time.perf_counter()

        # Create the function to get these values
        # the query for this is stored in `.queries` as Enum
        await super().execute(_Queries.CLONE.value)
        # Get the constituent query from fetching with that function
        all_tables: Union[list[_Record], Iterator[str]] = await super().fetch(
            "SELECT * FROM generate_create_table_statement('.*');"
        )
        # Convert the list of `asyncpg.Record` into list of str
        # The sole column is generate_create_table_statement
        all_tables = map(lambda x: x["generate_create_table_statement"], all_tables)
        for table_reconstruction_sql in all_tables:
            # NOTE: This regex relies on the fact that we assume public
            # This is specific for this project.
            table_name = _re.search(  # type: ignore
                r"(?<=create\stable\s)\w{1,}",
                table_reconstruction_sql,
                flags=_re.IGNORECASE,
            ).group(0)
            # This will never be None

            print(f"Cloning table {table_name}...")
            # See if a similarly named table exists
            # If it does then drop it
            self._cursor.execute(
                _Template("DROP TABLE IF EXISTS $a").substitute(a=table_name)
            )
            # Cast the table structure
            self._cursor.execute(table_reconstruction_sql)
            # Get all the data for the associated table from the remote database
            table_items = await super().fetch(
                _Template("SELECT * FROM $a;").substitute(a=table_name)
            )
            # Convert `asyncpg.Record` -> tuple for passing it into sqlite3
            table_items = tuple(map(tuple, table_items))
            # Check if there is anything to insert into the sqlite3 db
            if not table_items:
                print(f"Table {table_name} is empty, skipping...")
                continue
            # That is the case, insert values into the sqlite3 db
            self._cursor.executemany(
                _Template("INSERT INTO $a VALUES ($b);").substitute(
                    a=table_name, b=", ".join(["?"] * len(table_items[0]))
                ),
                table_items,
            )
            print(f"Cloned table {table_name}, {len(table_items)} rows")
        self._lite_con.commit()
        print(f"Collected tables in {_time.perf_counter() - t_start} seconds")

    async def execute(self, query: str, *args, timeout: float = None) -> str:
        """
        Execute an SQL command (or commands).

        Pool performs this operation using one of its connections.  Other than
        that, it behaves identically to
        `Connection.execute() <asyncpg.connection.Connection.execute>`.
        This executes the identical query on the sqlite3 cache to preserve being synchronised

        Args:
            query (str): The query to be executed
            timeout (float, optional): timeout in seconds. Defaults to None.

        Returns:
            str: Status of the last SQL command that was performed on the remote database.
        """
        # NOTE: sqlite takes in Iterable[Any] but asyncpg takes in a variadic
        self._cursor.execute(query, args)
        r = await super().execute(query, *args, timeout=timeout)
        self._lite_con.commit()
        return r

    async def executemany(
        self, command: str, args: Iterable[Iterable[Any]], *, timeout: float = None
    ) -> None:
        """
        Execute an SQL command for each sequence of arguments in args.
        atomic operation, which means that either all executions succeed, or none at all

        Args:
            command (str): The query to be executed
            args (Iterable): An iterable of arguments to be passed to the query for execution
            timeout (float, optional): timeout in seconds. Defaults to None.
        """
        self._cursor.executemany(command, args)
        await super().executemany(command, args, timeout=timeout)
        self._lite_con.commit()

    def fetch(self, query: str, *args) -> list[Any]:
        """
        Fetch rows from local cache.
        As such, this is a synchronous operation.

        Args:
            query (str): The query to be executed

        Returns:
            list[Any]: List of rows returned by the query
        """
        return self._cursor.execute(query, args).fetchall()

    def fetchone(self, query, *args) -> Any:
        """
        Fetch the first row from local cache.
        As such, this is a synchronous operation.

        Args:
            query (str): The query to be executed

        Returns:
            Any: The first row returned by the query, or None if no rows were found"""
        return self._cursor.execute(query, args).fetchone()

    def __await__(self):
        yield from super().__await__()
        yield from self.pull().__await__()
        return self

    def __aenter__(self):
        raise NotImplementedError


def create_caching_pool(*args, **kwargs) -> LiteCache:
    """
    Returns an instance of LiteCache with the provided arguments and keyword arguments.
    Similar to asyncpg's create_pool

    Returns:
        LiteCache: An instance of LiteCache class with the provided arguments and keyword arguments
    """
    return LiteCache(*args, **kwargs)
