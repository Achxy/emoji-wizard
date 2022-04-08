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
import sqlite3
from typing import ClassVar

import asyncpg
from asyncpg import connection, protocol

from queries import Queries


class ALiteCache(asyncpg.Pool):
    """
    A wrapper around `asyncpg.Pool` that provides a cache for queries.
    """

    __slots__: ClassVar[tuple[str, ...]] = (
        "__con",
        "__cur",
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
        self.__con = sqlite3.connect(":memory:")
        self.__cur = self.__con.cursor()
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

    async def pull(self) -> None:
        """
        Pulls the latest data from the database and stores it in sqlite3 memory.
        """
        self.__con = sqlite3.connect(":memory:")
        self.__cur = self.__con.cursor()

        await super().execute(Queries.CLONER.value)
        tables = await super().fetch(Queries.GET_SCHEMA_PUBLIC_TABLES.value)

        for tble in tables:
            table_name = tble["table_name"]
            table_creator = await super().fetch(
                "SELECT * FROM generate_create_table_statement($1);", table_name
            )
            self.__cur.execute(table_creator[0]["generate_create_table_statement"])

            remote_contents = await super().fetch(f"SELECT * FROM {table_name}")
            if not remote_contents:
                continue
            local_query = f"INSERT INTO {table_name} VALUES ({','.join(['?'] * len(remote_contents[0]))});"
            self.__cur.executemany(local_query, remote_contents)

        self.__con.commit()
        self.__pull_complete = True

    async def do_pull_if_not_complete(self):
        """
        Completes `pull` if it is not complete atleast once.
        """
        if not self.__pull_complete:
            await self.pull()

    async def execute(self, query: str, *args, timeout: float | None = None):
        """
        Executes a query on the database and then acts on the cache
        then commits the changes.

        Args:
            query (str): The query to execute.
            timeout (float | None, optional): Time it should take to complete the query. Defaults to None.
        """
        await self.do_pull_if_not_complete()
        ret = await super().execute(query, *args, timeout=timeout)  # type: ignore
        self.__cur.execute(query, args)
        self.__con.commit()
        return ret

    async def executemany(self, command: str, args, *, timeout: float | None = None):
        """
        Executes the command the by iterating over each argument and then acts on the cache
        then commits the changes.

        Args:
            command (str): The command to execute.
            args (_type_): The arguments to execute the command with.
            timeout (float | None, optional): Time it should take to complete the query. Defaults to None.
        """
        await self.do_pull_if_not_complete()
        ret = await super().executemany(command, args, timeout=timeout)  # type: ignore
        self.__cur.executemany(command, args)
        self.__con.commit()
        return ret

    async def fetch(self, query: str, *args, timeout: float | None = None):
        """
        Fetches the value from cache and returns in

        Args:
            query (str): The query to execute.
            args (_type_): The arguments to execute the command with.

        Returns:
            _type_: The value returned from the cache.
        """
        await self.do_pull_if_not_complete()
        return self.__cur.execute(query, args).fetchall()

    async def fetchrow(self, query: str, *args, timeout: float | None = None):
        """
        Fetches the value from cache and returns the first row in the result.

        Args:
            query (str): The query to execute.
            timeout (float | None, optional): Time it should take to complete the query. Defaults to None.

        Returns:
            _type_: The first row returned from the cache.
        """
        await self.do_pull_if_not_complete()
        return self.__cur.execute(query, args).fetchone()

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
    """
    Instantiates `ALiteCache` with the given parameters.
    and then awaits it and returns the instance.
    """
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
