import asyncpg
import discord
from tools.bot_tools import get_default_prefix
from tools.enum_tools import TableType
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

        # Table for storing emoji rubric stats
        query = """CREATE TABLE IF NOT EXISTS emoji_rubric(
                    guild_id BIGINT,
                    channel_id BIGINT,
                    user_id BIGINT,
                    type_of_rubric TEXT,
                    usage_count BIGINT
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
        self,
        ctx,
        command_or_rubric_name,
        table: Union[TableType, str],
        value_to_increment=1,
    ):
        if isinstance(table, TableType):
            table = table.value

        # See if the record of user exist in database
        if table == "usage":
            column = "type_of_cmd"
        elif table == "emoji_rubric":
            column = "type_of_rubric"
            command_or_rubric_name += ":rubric"
        else:
            raise ValueError(f"Table {table} doesn't exist")

        query = f"""SELECT usage_count FROM {table}
                    WHERE (
                        guild_id = $1 AND
                        channel_id = $2 AND
                        user_id = $3 AND
                        {column} = $4
                    );
                """
        count = await self.pool.fetch(
            query, ctx.guild.id, ctx.channel.id, ctx.author.id, command_or_rubric_name
        )
        if not count:
            # Row didn't use to exist
            # Create it
            query = f"""INSERT INTO {table} (
                        guild_id,
                        channel_id,
                        user_id,
                        {column},
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
            await self.pool.execute(
                query,
                ctx.guild.id,
                ctx.channel.id,
                ctx.author.id,
                command_or_rubric_name,
                value_to_increment,
            )
            return

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

        await self.pool.execute(
            query,
            count + value_to_increment,
            ctx.guild.id,
            ctx.channel.id,
            ctx.author.id,
            command_or_rubric_name,
        )
