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

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, new_prefix):
        query = "UPDATE guilds SET prefix = $1 WHERE guild_id = $2"
        await self.bot.db.execute(query, new_prefix, ctx.guild.id)
        await ctx.send("Successfully set prefix")


def setup(bot):
    bot.add_cog(meta(bot))
