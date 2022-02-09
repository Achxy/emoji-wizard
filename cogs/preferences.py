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


def setup(bot):
    bot.add_cog(Preferences(bot))
