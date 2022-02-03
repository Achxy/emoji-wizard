import discord
from discord.ext import commands
from tools.enum_tools import TableType


class RemoveAll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def remove_all(self, ctx):
        """
        Takes no parameters, removes all emojis from the server
        """

        count = 0
        for each_emoji in ctx.guild.emojis:
            count += 1
            try:
                await each_emoji.delete()
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass
            else:
                embed = discord.Embed(
                    title="Success!",
                    description=f"Removed **{each_emoji}** from the server",
                )
                embed.set_footer(text=f"{len(ctx.guild.emojis)} more to go")
                await ctx.send(embed=embed)

        await self.bot.tools.increment_usage(
            ctx, __import__("inspect").stack()[0][3], TableType.command
        )
        await self.bot.tools.increment_usage(
            ctx,
            f"{__import__('inspect').stack()[0][3]}:{ctx.command.name}",
            TableType.rubric,
            count,
        )


def setup(bot):
    bot.add_cog(RemoveAll(bot))
