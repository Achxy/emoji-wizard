import discord
import typing
from discord.ext import commands
from tools.enum_tools import TableType


class Enlarge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def enlarge(self, ctx, *emotes: typing.Union[discord.PartialEmoji, str]):

        successful_additions = 0

        for index, i in enumerate(emotes):

            if not isinstance(i, discord.PartialEmoji):
                embed = discord.Embed(
                    title="That is not an custom emoji",
                    description=f"You need to give me an custom discord emoji!\nYou passed in : {i}",
                )
                await ctx.send(embed=embed)
                continue

            embed = discord.Embed(title=f"Enlarged view of {i.name}")
            embed.set_image(url=i.url)
            embed.set_footer(
                text=f"{index + 1} of {len(emotes)} to enlarge {'' if not (index + 1) == len(emotes) else '(over)'}"
            )

            successful_additions += 1
            await ctx.send(embed=embed)

        await self.bot.tools.increment_usage(
            ctx, __import__("inspect").stack()[0][3], TableType.command
        )
        await self.bot.tools.increment_usage(
            ctx,
            f"{__import__('inspect').stack()[0][3]}:{ctx.command.name}",
            TableType.rubric,
            successful_additions,
        )


def setup(bot):
    bot.add_cog(Enlarge(bot))
