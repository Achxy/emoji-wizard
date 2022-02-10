import discord
from typing import Union, Callable
from discord.ext import commands
from tools.enum_tools import TableType
from tools.bot_tools import page_index
from utilities.preference import Preference


class Enlarge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @Preference.is_usable
    async def enlarge(self, ctx, *emotes: Union[discord.PartialEmoji, str]):

        successful_additions: int = 0
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

            successful_additions += 1
            await ctx.send(embed=embed)

        await self.bot.tools.increment_usage(ctx, TableType.command)
        await self.bot.tools.increment_usage(
            ctx,
            TableType.rubric,
            successful_additions,
        )


def setup(bot):
    bot.add_cog(Enlarge(bot))
