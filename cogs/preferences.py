import discord
from discord.ext import commands
from tools.database_tools import Actions
from typing import Optional


class PreferencesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ignore(self, ctx, channel: Optional[discord.TextChannel] = None):
        """
        Ignores a text channel(s)
        This command will work regardless of whether the channel is ignored.
        """
        await self.bot.tools.ignore_channel(ctx.guild.id, channel.id)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unignore(self, ctx, channel: Optional[discord.TextChannel] = None):
        """
        Unignores a text channel(s)
        This command will work regardless of whether the channel is ignored.
        """
        await self.bot.tools.channel_action(ctx, Actions.unignore, channel)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def enable(self, ctx, command_name: str):
        """
        Enables a command
        This command will work regardless of whether the channel is ignored.
        """

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx, command_name: str):
        """
        Disables a command
        This command will work in regardless of whether the channel is ignored.
        """


def setup(bot):
    bot.add_cog(PreferencesCog(bot))
