from __future__ import annotations

import asyncpg as _asyncpg
import sqlite3 as _sqlite3

import time
import re
from enum import Enum as _Enum
from .queries import Queries as _Queries
from string import Template as _Template
from asyncpg import connection as _connection, protocol as _protocol, Record as _Record
from typing import Any, Iterator


__all__: tuple[str, ...] = (
    "Bound",
    "LiteCache",
    "create_caching_pool",
)


class Bound(_Enum):
    MEMORY = 0
    DISK = 1


class LiteCache(_asyncpg.Pool):
    def __init__(
        self,
        dsn=None,
        bounding: Bound = Bound.MEMORY,
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
    ):

        if not isinstance(bounding, Bound):
            raise TypeError(f"bounding must be of type Bound, got {type(bounding)}")

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
        self._bounding = bounding
        self._lite_con = (
            _sqlite3.connect(":memory:")
            if bounding is Bound.MEMORY
            else _sqlite3.connect("TODO.db")  # TODO:
        )
        self._cursor = self._lite_con.cursor()

    async def pull(self):
        print("Collecting tables...")
        t_start = time.perf_counter()

        await super().execute(_Queries.CLONE.value)
        all_tables: list[_Record] = await super().fetch(
            "SELECT * FROM generate_create_table_statement('.*');"
        )
        all_tables: Iterator[str] = map(
            lambda x: x["generate_create_table_statement"], all_tables
        )
        for table_reconstruction_sql in all_tables:
            table_name = re.search(
                r"(?<=create\stable\s)\w{1,}",
                table_reconstruction_sql,
                flags=re.IGNORECASE,
            ).group()
            print(f"Cloning table {table_name}...")
            self._cursor.execute(table_reconstruction_sql)
            table_items = await super().fetch(
                _Template("SELECT * FROM $a;").substitute(a=table_name)
            )
            table_items = tuple(map(tuple, table_items))
            if not table_items:
                print(f"Table {table_name} is empty, skipping...")
                continue
            self._cursor.executemany(
                _Template("INSERT INTO $a VALUES ($b);").substitute(
                    a=table_name, b=", ".join(["?"] * len(table_items[0]))
                ),
                table_items,
            )
            print(f"Cloned table {table_name}, {len(table_items)} rows")
        self._lite_con.commit()
        print(f"Collected tables in {time.perf_counter() - t_start} seconds")

    async def execute(self, query: str, *args, timeout: float = None) -> str:
        self._cursor.execute(query, args)
        r = await super().execute(query, *args, timeout=timeout)
        self._lite_con.commit()
        return r

    async def executemany(self, command: str, args, *, timeout: float = None):
        self._cursor.executemany(command, args)
        r = await super().executemany(command, args, timeout=timeout)
        self._lite_con.commit()
        return r

    def fetch(self, query: str, *args) -> list[Any]:
        return self._cursor.execute(query, args).fetchall()

    def fetchone(self, query, *args) -> tuple:
        return self._cursor.execute(query, args).fetchone()

    def __await__(self):
        yield from super().__await__()
        yield from self.pull().__await__()
        return self


def create_caching_pool(*args, **kwargs) -> LiteCache:
    return LiteCache(*args, **kwargs)
