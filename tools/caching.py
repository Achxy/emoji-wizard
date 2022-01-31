import asyncpg
import discord
from tools.database_tools import increment_usage


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

    async def command(
        self, ctx: discord.ext.commands.context.Context, type_of_command: str
    ):
        """
        Accepts 2 positional arguments, command context and type of command (str) respectively
        returns None
        Internally references increment_usage from database_tools
        """
        await increment_usage(self.pool, ctx, type_of_command, 1)
