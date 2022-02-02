import asyncpg
import discord
from enum_tools import TableType


class Tables:
    def __init__(self, bot: discord.ext.commands.bot.Bot, table: TableType):
        self.bot = bot
        self.pool: asyncpg.pool.Pool = self.bot.db
        self.table = table.value
        self.rows = []

    async def populate(self):
        """
        Get all the rows from the table and assign it to self.rows
        """
        self.rows = []
        for each_row in await self.pool.fetch(f"SELECT * FROM {self.table}"):
            self.rows.append(each_row)

    async def append(self, new_list):
        """
        index 0: guild_id
        index 1: channel_id
        index 2: user_id
        index 3: type
        index 4: usage

        If index 0-3 matches a record then usage will be incremented to the existing record
        """
        for index, i in enumerate(self.rows):
            if i[:4] == new_list[:4]:
                self.rows[index][4] += new_list[4]
                return
        self.rows.append(new_list)

    async def reset(self):
        self.rows = []

    @property
    def row_count(self):
        return len(self.rows)

    @property
    def get_row(self):
        return self.rows
