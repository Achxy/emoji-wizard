import disnake
from disnake.ext import commands
from tools.enum_tools import TableType
from utilities.preference import Preference


class RemoveAll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    @Preference.is_usable
    async def remove_all(self, ctx):
        """
        Takes no parameters, removes all emojis from the server
        """

        count: int = 0
        for each_emoji in ctx.guild.emojis:
            count += 1
            try:
                await each_emoji.delete()
            except disnake.Forbidden:
                pass
            except disnake.HTTPException:
                pass
            else:
                embed = disnake.Embed(
                    title="Success!",
                    description=f"Removed **{each_emoji}** from the server",
                )
                embed.set_footer(text=f"{len(ctx.guild.emojis)} more to go")
                await ctx.send(embed=embed)

        await self.bot.tools.increment_usage(
            ctx,
            TableType.rubric,
            count,
        )


def setup(bot):
    bot.add_cog(RemoveAll(bot))
