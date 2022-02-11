import discord
from discord.ext import commands
from tools.database_tools import Actions
from typing import Union


class PreferencesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ignore(self, ctx, *channels: Union[discord.TextChannel, int, str]):
        """
        Ignores a text channel(s)
        This command will work regardless of whether the channel is ignored.
        """

        for each_channel in channels:
            await self.bot.tools.channel_action(ctx, Actions.ignore, each_channel)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unignore(self, ctx, *channel: Union[discord.TextChannel, int, str]):
        """
        Unignores a text channel(s)
        This command will work regardless of whether the channel is ignored.
        """

        for each_channel in channel:
            await self.bot.tools.channel_action(ctx, Actions.unignore, each_channel)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def enable(ctx, command_name: str):
        """
        Enables a command
        This command will work regardless of whether the channel is ignored.
        """

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def disable(ctx, command_name: str):
        """
        Disables a command
        This command will work in regardless of whether the channel is ignored.
        """


def setup(bot):
    bot.add_cog(PreferencesCog(bot))
