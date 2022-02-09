import discord
from discord.ext import commands
from tools.database_tools import Actions
from typing import Union


class Preferences(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ignore(self, ctx, *channels: Union[discord.TextChannel, int, str]):
        """
        Ignores a text channel(s)
        This command will work in regardless of whether the channel is ignored.
        """

        for each_channel in channels:
            await self.bot.tools.channel_action(ctx, Actions.ignore, each_channel)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unignore(self, ctx, *channel: Union[discord.TextChannel, int, str]):
        """
        Unignores a text channel(s)
        This command will work in regardless of whether the channel is ignored.
        """

        for each_channel in channel:
            await self.bot.tools.channel_action(ctx, Actions.unignore, each_channel)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def enable(self, ctx, *command: commands.Command):
        """
        Enables a command(s)
        """
        for each_command in command:
            if each_command not in filter(
                lambda x: not x.hidden, [cmd.name for cmd in self.bot.commands]
            ):
                # The command does not exist
                await ctx.send(f"Command **{each_command}** does not exist")
                continue
            # Check if the command is already enabled
            if await self.bot.tools.is_enabled(ctx.guild.id, each_command.name):
                await ctx.send(f"Command **{each_command}** is already enabled")
                continue
            # Now we can safely enable the command
            await self.bot.tools.enable_command(ctx.guild.id, each_command.name)
            # Now we can send a message to the channel
            await ctx.send(f"Successfully enabled command **{each_command}**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx, *command: commands.Command):
        """
        Disables a command(s)
        """
        for each_command in command:
            if each_command not in filter(
                lambda x: not x.hidden, [cmd.name for cmd in self.bot.commands]
            ):
                # The command does not exist
                await ctx.send(f"Command **{each_command}** does not exist")
                continue
            # Check if the command is already disabled
            if not await self.bot.tools.is_enabled(ctx.guild.id, each_command.name):
                await ctx.send(f"Command **{each_command}** is already disabled")
                continue
            # Now we can safely disable the command
            await self.bot.tools.disable_command(ctx.guild.id, each_command.name)
            # Now we can send a message to the channel
            await ctx.send(f"Successfully disabled command **{each_command}**")


def setup(bot):
    bot.add_cog(Preferences(bot))
