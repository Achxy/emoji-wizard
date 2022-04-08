from typing import ClassVar
import asyncpg
import sqlite3
from asyncpg import protocol, connection
from .queries import Queries


class ALiteCache(asyncpg.Pool):
    __slots__: ClassVar[tuple[str, ...]] = (
        "con",
        "cur",
        "__pull_complete",
    )

    def __init__(
        self,
        *connect_args,
        min_size,
        max_size,
        max_queries,
        max_inactive_connection_lifetime,
        setup,
        init,
        loop,
        connection_class,
        record_class,
        **connect_kwargs,
    ) -> None:
        self.con = sqlite3.connect(":memory:")
        self.cur = self.con.cursor()
        self.__pull_complete = False
        super().__init__(
            *connect_args,
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

    async def pull(self):
        self.con = sqlite3.connect(":memory:")
        self.cur = self.con.cursor()

        await super().execute(Queries.CLONER.value)
        tables = await super().fetch(Queries.GET_SCHEMA_PUBLIC_TABLES.value)

        for t in tables:
            table_name = t["table_name"]
            table_creator = await super().fetch(
                "SELECT * FROM generate_create_table_statement($1);", table_name
            )
            self.cur.execute(table_creator[0]["generate_create_table_statement"])

            # Prevent any possible SQL injection
            # Although this is completely safe
            # TODO: ...
            remote_contents = await super().fetch(f"SELECT * FROM {table_name}")
            if not remote_contents:
                continue
            local_query = f"INSERT INTO {table_name} VALUES ({','.join(['?'] * len(remote_contents[0]))});"
            self.cur.executemany(local_query, remote_contents)

        self.con.commit()
        self.__pull_complete = True

    async def do_pull_if_not_complete(self):
        if not self.__pull_complete:
            await self.pull()

    async def execute(self, query: str, *args, timeout: float | None = None):
        await self.do_pull_if_not_complete()
        r = await super().execute(query, *args, timeout=timeout)  # type: ignore
        self.cur.execute(query, args)
        self.con.commit()
        return r

    async def executemany(self, command: str, args, *, timeout: float | None = None):
        await self.do_pull_if_not_complete()
        r = await super().executemany(command, args, timeout=timeout)  # type: ignore
        self.cur.executemany(command, args)
        self.con.commit()
        return r

    async def fetch(self, query: str, *args, timeout: float | None = None):
        await self.do_pull_if_not_complete()
        return self.cur.execute(query, args).fetchall()

    async def fetchrow(self, query: str, *args, timeout: float | None = None):
        await self.do_pull_if_not_complete()
        return self.cur.execute(query, args).fetchone()

    def __await__(self):
        yield from super().__await__()
        yield from self.pull().__await__()
        return self


async def create_caching_pool(
    dsn=None,
    *,
    min_size=10,
    max_size=10,
    max_queries=50000,
    max_inactive_connection_lifetime=300.0,
    setup=None,
    init=None,
    loop=None,
    connection_class=connection.Connection,
    record_class=protocol.Record,
    **connect_kwargs,
) -> ALiteCache:
    ret = ALiteCache(
        dsn,
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
    await ret
    return ret
