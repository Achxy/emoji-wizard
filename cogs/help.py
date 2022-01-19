import discord
from discord.ext import commands


class help_(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(ctx):
        return


def setup(bot):
    bot.add_cog(help_(bot))
