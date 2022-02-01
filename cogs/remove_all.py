import discord
from discord.ext import commands
from tools.database_tools import increment_usage


class remove_all(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def remove_all(self, ctx):
        """
        Takes no parameters, removes all emojis from the server
        """
        cmd_type = "cmd_remove_all"
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

        await increment_usage(self.bot, ctx, cmd_type, count)


def setup(bot):
    bot.add_cog(remove_all(bot))
