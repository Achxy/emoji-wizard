import asyncpg
import disnake as discord
from disnake.ext import commands
from enum import Enum
from typing import Union
from tools.enum_tools import TableType
from tools.caching import InterpolateAction


__all__ = (
    "DatabaseTools",
    "Actions",
)

INEPT = object()


class Actions(Enum):
    """
    Enum for the different actions that can be done with the database
    switches for ignoring and unignoring channels and commands
    """

    ignore = 1
    unignore = 2
    enable = unignore
    disable = ignore


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

        # Table for storing command preferences
        query = """CREATE TABLE IF NOT EXISTS command_preferences(
                    guild_id BIGINT,
                    ignored_command TEXT
                    );
                """
        await self.pool.execute(query)

        # Table for storing channel preferences
        query = """CREATE TABLE IF NOT EXISTS channel_preferences(
                    guild_id BIGINT,
                    channel_id BIGINT
                    );
                """
        await self.pool.execute(query)

    async def increment_usage(
        self,
        ctx,
        table: Union[TableType, str],
        value_to_increment: int = 1,
    ) -> None:
        """
        This function is used to increment the usage count of a command or emoji actions (ie, emoji rubric)
        Function name will be taken from ctx, this is what that will be logged into the database
        if the table is of instance TableType.rubric then :rubric will be appended to the end of the function name
        """

        if isinstance(table, TableType):
            table_ = table  # Keep one former copy
            table = table.value

        command_or_rubric_name = ctx.command.name

        # See if the record of user exist in database
        if table == "usage":
            column = "type_of_cmd"
        elif table == "emoji_rubric":
            column = "type_of_rubric"
            command_or_rubric_name += ":rubric"
        else:
            raise ValueError(f"Table {table} doesn't exist")

        # Interpolate the data to existing cache
        # Both command and rubric interpolation should be of type coinciding
        # So there isn't a need to make another check
        rows = [ctx.guild.id, ctx.channel.id, ctx.author.id, command_or_rubric_name]
        self.bot.cache.interpolate(
            table_, rows, InterpolateAction.coincide, value_to_increment
        )

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

    def is_preferred(self, ctx, table: TableType, entity):
        assert isinstance(table, TableType)
        # entity is either a channel or a command
        # We need to check if the channel or command is preferred
        for values in filter(
            lambda x: x[0] == ctx.guild.id, self.bot.cache.get_cache(table)
        ):
            # values is a list containing two elements
            # 0 -> guild_id (We are filtering where guild_id = ctx.guild.id)
            # 1 -> channel_id or command_name
            if values[1] == entity:
                return False  # If this is in the cache, it is not preferred
        return True

    async def channel_action(self, ctx, action: Actions, channel):
        """
        This function is used to enable or disable a channel in the guild
        """
        assert isinstance(action, Actions)
        if not isinstance(channel, discord.TextChannel):
            return await ctx.send("That channel was not found")
        # We have a valid channel
        # Check if the channel's origin matches that of ctx.guild
        if not channel.guild == ctx.guild:
            return await ctx.send(
                "That channel was not found"
            )  # Indistinguishable message for privacy
        # Check if the channel is already ignored / unignored
        if action is Actions.ignore and self.is_preferred(
            ctx, TableType.channel, channel
        ):
            return await ctx.send(f"That {channel.mention} is already ignored")
        if action is Actions.unignore and not self.is_preferred(
            ctx, TableType.channel, channel
        ):
            return await ctx.send(
                f"That {channel.mention} is not ignored to begin with!"
            )
        # All good to go
        # Check if the action is to enable or disable
        # Appropriatly cache the action
        rows = [ctx.guild.id, channel.id]

        if action is Actions.ignore:
            query = """INSERT INTO channel_preferences (guild_id, channel_id)
                        VALUES ($1, $2);"""

            self.bot.cache.interpolate(
                TableType.channel_preference, rows, InterpolateAction.append
            )
            await self.pool.execute(query, *rows)
            return await ctx.send(f"Channel {channel.mention} has been ignored")

        elif action is Actions.unignore:
            # Can be written outside elif, this is for readability
            query = """DELETE FROM channel_preferences
                        WHERE guild_id = $1 AND channel_id = $2;"""

            self.bot.cache.interpolate(
                TableType.channel_preference, rows, InterpolateAction.destruct
            )
            await self.pool.execute(query, *rows)
            return await ctx.send(f"Channel {channel.mention} has been unignored")

    async def command_action(self, ctx, action: Actions, command):
        """
        This function is used to enable or disable a command in the guild
        """
        assert isinstance(action, Actions)
        if command.lower() not in map(
            lambda y: y.name.lower(), filter(lambda x: not x.hidden, self.bot.commands)
        ):
            return await ctx.send("That command was not found")
        # We have a valid command
        # Just add it to the cache and database
        # Check if the command is already ignored / unignored
        if action is Actions.enable and self.is_preferred(
            ctx, TableType.command_preference, command
        ):
            return await ctx.send(f"`{command}` is already enabled")
        if action is Actions.disable and not self.is_preferred(
            ctx, TableType.command_preference, command
        ):
            return await ctx.send(f"`{command}` is already disabled")
        # All good to go
        # Check if the action is to enable or disable
        rows = [ctx.guild.id, command]
        if action is Actions.disable:
            query = """INSERT INTO command_preferences (guild_id, ignored_command)
                        VALUES ($1, $2);"""

            self.bot.cache.interpolate(
                TableType.command_preference, rows, InterpolateAction.append
            )
            await self.pool.execute(query, *rows)
            return await ctx.send(f"Command `{command}` has been disabled")
        if action is Actions.enable:
            query = """DELETE FROM command_preferences
                        WHERE guild_id = $1 AND ignored_command = $2;"""

            self.bot.cache.interpolate(
                TableType.command_preference, rows, InterpolateAction.destruct
            )
            await self.pool.execute(query, *rows)
            return await ctx.send(f"Command `{command}` has been enabled")
