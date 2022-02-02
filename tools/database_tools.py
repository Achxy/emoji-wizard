import asyncpg
import discord
from tools.bot_tools import get_default_prefix
from tools.enum_tools import CommandType, EmojiRubric
from typing import Union, Optional


async def confirm_tables(pool: asyncpg.pool.Pool):
    """
    Takes an asyncpg.pool.Pool object as sole argument
    returns None

    The purpose of this is to create required tables if they don't exist
    This will make the bot very plug-and-play friendly
    """
    # Table for storing custom prefix
    query = """CREATE TABLE IF NOT EXISTS guilds (
                guild_id BIGINT,
                prefix TEXT
                );
            """
    await pool.execute(query)

    # Table for storing bot usage stats
    query = """CREATE TABLE IF NOT EXISTS usage (
                -- We would like to have each user's usage in each channel and in each guild
                guild_id BIGINT,
                channel_id BIGINT,
                user_id BIGINT,
                type_of_cmd TEXT,
                usage_count INT

            );
            """
    await pool.execute(query)


async def increment_usage(
    bot: discord.ext.commands.bot.Bot,
    ctx: discord.ext.commands.context.Context,
    type_of_cmd_or_rubric: Union[CommandType, EmojiRubric],
    value_to_increment: Optional[int] = None,
    with_caching=True,
):
    """
    Takes a bot object, a context object, a type of command or a rubric and a value to increment
    raises TypeError if the type of command or rubric is not of type CommandType or EmojiRubric
    returns None
    """

    # There is no need to log anything to db or cache
    if value_to_increment == 0:
        return

    pool: asyncpg.pool.Pool = bot.db

    # It is to be noted that value_to_increment is optional when it is command type
    # This is because we want to increment usage of a command by 1
    # But we want to increment usage of a rubric by a value
    # Therefore if value_to_increment is None and type_of_cmd_or_rubric is EmojiRubric we will raise TypeError
    if isinstance(type_of_cmd_or_rubric, CommandType):
        type_of_cmd = type_of_cmd_or_rubric.value
        if value_to_increment is None:
            value_to_increment = 1
    elif isinstance(type_of_cmd_or_rubric, EmojiRubric):
        type_of_cmd = type_of_cmd_or_rubric.value
        if value_to_increment is None:
            raise TypeError("Value to increment is not provided for EmojiRubric")
    else:
        raise TypeError(
            "type_of_cmd_or_rubric must be either CommandType or EmojiRubric"
        )

    # Table that we are acting upon depends on the type of command or rubric
    if isinstance(type_of_cmd_or_rubric, CommandType):
        table = "usage"
        type_column = "type_of_cmd"
    else:
        table = "emoji_rubric"
        type_column = "type_of_rubric"

    if with_caching:
        # We want to cache the usage count or rubric count
        # Check what we are trying to increment is a command or a rubric
        if isinstance(type_of_cmd_or_rubric, CommandType):
            # We are incrementing a command
            # Check if the command is already in cache
            if type_of_cmd in bot.cache.cmd_cache.keys():
                # We already have the command in cache
                # Increment the usage count
                bot.cache.cmd_cache[type_of_cmd] += value_to_increment
            else:
                # We don't have the command in cache
                # Fetch the sum of usage count from db where type_of_cmd = type_of_cmd
                query = f"SELECT SUM(usage_count) FROM {table} WHERE {type_column}= $1"
                r = await pool.fetch(query, type_of_cmd)
                r = r[0].get("sum")
                if r is None:
                    r = 0
                bot.cache.cmd_cache[type_of_cmd] = int(r) + value_to_increment
        else:
            # We are incrementing a rubric
            # Check if the rubric is already in cache
            if type_of_cmd in bot.cache.cmd_cache.keys():
                # We already have the rubric in cache
                # Increment the usage count
                bot.cache.rubric_cache[type_of_cmd] += value_to_increment
            else:
                # We don't have the rubric in cache
                # Fetch the sum of usage count from db where type_of_cmd = type_of_cmd
                query = f"SELECT SUM(usage_count) FROM {table} WHERE {type_column} = $1"
                r = await pool.fetch(query, type_of_cmd)
                r = r[0].get("sum")
                if r is None:
                    r = 0
                bot.cache.rubric_cache[type_of_cmd] = int(r) + value_to_increment

    # See if the record of user exist in database
    query = f"""SELECT usage_count FROM {table}
                WHERE (
                    guild_id = $1 AND
                    channel_id = $2 AND
                    user_id = $3 AND
                    {type_column} = $4
                );
            """

    count = await pool.fetch(
        query, ctx.guild.id, ctx.channel.id, ctx.author.id, type_of_cmd
    )

    if not count:
        # Row didn't use to exist
        # Create it
        query = f"""INSERT INTO {table} (
                    guild_id,
                    channel_id,
                    user_id,
                    {type_column},
                    usage_count
                    )
                    VALUES (
                        $1,
                        $2,
                        $3,
                        $4,
                        $5
                    );
                """
        await pool.execute(
            query,
            ctx.guild.id,
            ctx.channel.id,
            ctx.author.id,
            type_of_cmd,
            value_to_increment,
        )
    else:
        # The row does exist
        # Which means a same user has previously used the comamnd on the same guild on the same channel
        # Increment the existing count with that of the successful additions

        # Get the integer value of usage_count from the response object
        count = int(count[0].get("usage_count"))

        # Update the existing value of usage_count to be count + successful additions
        query = f"""UPDATE {table}
                    SET usage_count = $1
                    WHERE (
                        guild_id = $2 AND
                        channel_id = $3 AND
                        user_id = $4 AND
                        {type_column} = $5
                    );
                """

        await pool.execute(
            query,
            count + value_to_increment,
            ctx.guild.id,
            ctx.channel.id,
            ctx.author.id,
            type_of_cmd,
        )


async def get_prefix_for_guild(
    pool: asyncpg.pool.Pool,
    guild: discord.guild.Guild,
    place_hold_with=get_default_prefix(),
):
    query = "SELECT prefix FROM guilds WHERE guild_id = $1"
    prefix = await pool.fetch(query, guild.id)

    if len(prefix) == 0:
        return place_hold_with
    else:
        return prefix[0].get("prefix")


async def get_usage_of(pool: asyncpg.pool.Pool, cmd: str = "global"):

    if cmd.lower() == "global":
        query = "SELECT SUM(usage_count) FROM usage"
        r = await pool.fetch(query)
        r = r[0].get("sum")
        return int(r)

    query = "SELECT SUM(usage_count) FROM usage WHERE type_of_cmd = $1"
    r = await pool.fetch(query, cmd)
    r = r[0].get("sum")
    assert r is not None  # We do not want to return None value just interrupt execution
    return int(r)
