import asyncpg



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
                cmd_type TEXT,
                usage_count INT

            );
            """
    await pool.execute(query)
