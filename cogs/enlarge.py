import disnake as discord
from disnake import PartialEmoji
from typing import Callable
from disnake.ext import commands
from tools.bot_tools import page_index


class Enlarge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def enlarge(self, ctx, *emotes: PartialEmoji | str):

        footer_enumer: Callable[[int], str] = page_index("enlarge", len(emotes))

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
            embed.set_footer(text=footer_enumer(index))

            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Enlarge(bot))
