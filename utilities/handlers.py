import disnake as discord
from disnake.ext import commands
from tools.enum_tools import TableType


class Handler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        await self.bot.tools.increment_usage(ctx, TableType.command)


def setup(bot):
    bot.add_cog(Handler(bot))
