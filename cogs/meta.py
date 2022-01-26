import discord
from discord.ext import commands
from database_tools import increment_usage


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

        cmd_type = "cmd_setprefix"

        query = "SELECT prefix FROM guilds WHERE guild_id = $1"
        old_prefix = await self.bot.db.fetch(query, ctx.guild.id)
        old_prefix = old_prefix[0].get("prefix")

        query = "UPDATE guilds SET prefix = $1 WHERE guild_id = $2"
        await self.bot.db.execute(query, new_prefix, ctx.guild.id)
        embed = discord.Embed(
            title="Successfully changed prefix",
            description=f"The old prefix used to be **{old_prefix}** now its **{new_prefix}**",
        )
        await ctx.send(embed=embed)
        await increment_usage(self.bot.db, ctx, cmd_type, 1)


def setup(bot):
    bot.add_cog(meta(bot))
