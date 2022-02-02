import discord
import typing
from discord.ext import commands
from tools.database_tools import increment_usage
from tools.enum_tools import CommandType, EmojiRubric


class enlarge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def enlarge_(self, ctx, *emotes: typing.Union[discord.PartialEmoji, str]):

        cmd_type = "cmd_enlarge"
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

        await increment_usage(self.bot, ctx, cmd_type, successful_additions)


def setup(bot):
    bot.add_cog(enlarge(bot))
