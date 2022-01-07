import discord
import typing
from discord.ext import commands


class enlarge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def enlarge_(self, ctx, *emotes: typing.Union[discord.PartialEmoji, str]):
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
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(enlarge(bot))
