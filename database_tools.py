import asyncpg
import discord


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
    pool: asyncpg.pool.Pool,
    ctx: discord.ext.commands.context.Context,
    type_of_cmd: str,
    value_to_increment: int,
):

    # There is no need to log anything to db
    if value_to_increment == 0:
        return

    # See if the record of user exist in database
    query = """SELECT usage_count FROM usage
                WHERE (
                    guild_id = $1 AND
                    channel_id = $2 AND
                    user_id = $3 AND
                    cmd_type = $4
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
                    cmd_type,
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
                        cmd_type = $5
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
