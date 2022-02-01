import asyncpg
import discord
from typing import Union, List, Any, Optional
from tools.bot_tools import flatten
from tools.database_tools import increment_usage
from tools.enum_tools import CommandType, EmojiRubric, DatabaseTables


class Tables:

    """
    Index 0: guild_id
    Index 1: channel_id
    Index 2: user_id
    Index 3: type_of_cmd_or_rubric
    Index 4: usage_count
    """

    def __init__(self) -> None:
        self.rows = []

    def retrieve_rows(
        self,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        user_id: Optional[int] = None,
        type_of_cmd_or_rubric=None,
        usage_count=None,
    ) -> List[List[Any]]:
        """
        Retrivies rows from the table that match the given parameters (if any)
        and returns them as a list of lists (rows)
        """
        # Check if all arguments are None, if it is then just return self.rows
        if not any([guild_id, channel_id, user_id, type_of_cmd_or_rubric, usage_count]):
            return self.rows
        # return the rows that match the given parameters, if None is given then it will be ignored
        return [
            each_row
            for each_row in self.rows
            if (guild_id is None or each_row[0] == guild_id)
            and (channel_id is None or each_row[1] == channel_id)
            and (user_id is None or each_row[2] == user_id)
            and (type_of_cmd_or_rubric is None or each_row[3] == type_of_cmd_or_rubric)
            and (usage_count is None or each_row[4] == usage_count)
        ]

    def add_row(self, *row_: List[Any]) -> None:
        """
        Index 0: guild_id
        Index 1: channel_id
        Index 2: user_id
        Index 3: type_of_cmd_or_rubric
        Index 4: usage_count

        If an record exist where all elements from 0 - 3 (inclusive) are matched then
        usage count will be incremented to the value of the last element (usage_count)
        """
        new_row = list(flatten(row_))
        for each_row in self.rows:
            if each_row[0:4] == new_row[0:4]:
                each_row[4] += new_row[4]
                return
        self.rows.append(new_row)
        print(self.retrieve_rows())  # FIXME: This is for debugging, remove it later

    def reset_rows(self):
        """
        Wipe all rows clean
        """
        self.rows = []

    def overwrite_rows(self):
        return  # FIXME: Yet to be implemented


class Cache:
    """
    IMPORTANT NOTE : Incrementing values in cache can write those values to the database
    This structure is to prevent repetitive code and to make caching and registering be done in single place
    This class can write to the database

    The purpose of this is to make the bot send as little requests as possible to database
    Which consequentially will make the bot work faster (as there isn't anything to fetch)
    To achieve this, bot will internally increment usage stat before registering them to database
    And will fetch the cache vars instead of fetching the database later on.

    Command usage and emoji usage rubric are cached seperately
    """

    def __init__(self, pool: asyncpg.pool.Pool) -> None:
        self.pool: asyncpg.pool.Pool = pool
        self.command_usage: Tables = Tables()
        self.emoji_rubric_usage: Tables = Tables()

    async def overwrite_cache(self) -> None:
        # Overwrite cache with database
        # Get values from database
        ...  # FIXME:

    async def emoji_rubric(
        self,
        ctx: discord.ext.commands.context.Context,
        type_of_rubric: EmojiRubric,
        value_to_increment,
    ):
        """
        Accepts 2 positional arguments, command context and type of rubric respectively
        returns None
        Internally references increment_usage from database_tools
        """

        self.emoji_rubric_usage.add_row(
            ctx.guild.id,
            ctx.channel.id,
            ctx.author.id,
            type_of_rubric.value,
            value_to_increment,
        )

        await increment_usage(
            self.pool,
            ctx,
            type_of_rubric.value,
            value_to_increment,
            in_the_table=DatabaseTables.rubric.value,
        )

    async def command(
        self, ctx: discord.ext.commands.context.Context, type_of_command: CommandType
    ):
        """
        Accepts 2 positional arguments, command context and type of command respectively
        returns None
        Internally references increment_usage from database_tools
        """

        self.command_usage.add_row(
            ctx.guild.id,
            ctx.channel.id,
            ctx.author.id,
            type_of_command.value,
            1,
        )

        await increment_usage(
            self.pool,
            ctx,
            type_of_command.value,
            1,
            in_the_table=DatabaseTables.command.value,
        )
