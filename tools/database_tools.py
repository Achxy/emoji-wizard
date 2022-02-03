import asyncpg
import discord
from tools.bot_tools import get_default_prefix
from typing import Union


class DatabaseTools:
    def __init__(self, bot: discord.ext.commands.bot.Bot):
        self.bot = bot
        self.pool = bot.db

    async def confirm_tables(self):
        """
        The purpose of this is to create required tables if they don't exist
        This will make the bot very plug-and-play friendly
        """
        # Table for storing custom prefix
        query = """CREATE TABLE IF NOT EXISTS guilds (
                        guild_id BIGINT,
                        prefix TEXT
                        );
                    """
        await self.pool.execute(query)

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
        await self.pool.execute(query)

    async def get_prefix_for_guild(
        self,
        guild: Union[discord.guild.Guild, int],
        place_hold_with=get_default_prefix(),
    ):
        if isinstance(guild, discord.guild.Guild):
            guild_id = guild.id
        else:
            guild_id = guild

        query = "SELECT prefix FROM guilds WHERE guild_id = $1"
        prefix = await self.pool.fetch(query, guild_id)

        if len(prefix) == 0:
            return place_hold_with
        else:
            return prefix[0].get("prefix")


async def increment_usage(
    bot: discord.ext.commands.bot.Bot,
    ctx: discord.ext.commands.context.Context,
    type_of_cmd: str,
    value_to_increment: int,
    with_caching=True,
):

    pool: asyncpg.pool.Pool = bot.db

    # There is no need to log anything to db or cache
    if value_to_increment == 0:
        return

    if with_caching:
        bot.usage_cache += value_to_increment

    # See if the record of user exist in database
    query = """SELECT usage_count FROM usage
                WHERE (
                    guild_id = $1 AND
                    channel_id = $2 AND
                    user_id = $3 AND
                    type_of_cmd = $4
                );
            """

    count = await pool.fetch(
        query, ctx.guild.id, ctx.channel.id, ctx.author.id, type_of_cmd
    )

    if not count:
        # Row didn't use to exist
        # Create it
        query = """INSERT INTO usage (
                    guild_id,
                    channel_id,
                    user_id,
                    type_of_cmd,
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
        query = """UPDATE usage
                    SET usage_count = $1
                    WHERE (
                        guild_id = $2 AND
                        channel_id = $3 AND
                        user_id = $4 AND
                        type_of_cmd = $5
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
