import discord
from discord.ext import commands


class meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        embed = discord.Embed(
            title="Pong! 🏓",
            description=f"Current Latency of the bot is {round(self.bot.latency * 1000)}ms",
        )
        await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(meta(bot))
