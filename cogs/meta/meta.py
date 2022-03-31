import discord
from discord.ext import commands


class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """
        Sends an embed with the bot's latency
        but really this command is just used to test the bot's responsiveness
        """
        embed = discord.Embed(
            title="Pong! 🏓",
            description=f"Current Latency of the bot is {round(self.bot.latency * 1000)}ms",
        )
        await ctx.reply(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, *, new_prefix: str):
        """
        Changes the bot's prefix for specific guilds
        """

        reason = (
            "too long\nMust be less than or equal to 8 characters"
            if len(new_prefix) > 8
            else "too short"
            if not new_prefix
            else None
        )

        if reason is not None:
            embed = discord.Embed(
                title="Cannot set that as prefix",
                description=f"The prefix you entered is {reason}",
            )
            return await ctx.reply(embed=embed)

        await self.bot.tools.set_prefix(ctx.guild.id, new_prefix)

        embed = discord.Embed(
            title="Successfully changed prefix",
            description=(
                f"The old prefix used to be **{ctx.prefix}** now its **{new_prefix}**\n"
                f"You can change it again by using `{new_prefix}setprefix` (pinging the bot works too!)\n\n"
                "```fix\n"
                f"{new_prefix}setprefix <new prefix>\n"
                "```"
            ),
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Meta(bot))
