import asyncpg
import discord
from tools.database_tools import increment_usage
from tools.enum_tools import CommandType


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
        self.pool = pool
        self.command_usage = 0
        self.emoji_rubric = 0

    async def overwrite_cache(self) -> None:
        return  # Implement later

    async def command(
        self, ctx: discord.ext.commands.context.Context, type_of_command: CommandType
    ):
        """
        Accepts 2 positional arguments, command context and type of command respectively
        returns None
        Internally references increment_usage from database_tools
        """
        print("im called")  # for debugging, remove afterwards, FIXME:
        self.command_usage += 1
        await increment_usage(self.pool, ctx, type_of_command.value, 1)
