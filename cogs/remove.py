import disnake as discord
from disnake.ext import commands
from typing import Union
from tools.enum_tools import TableType


class Remove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def remove(self, ctx, *emotes: Union[discord.Emoji, str]):

        successful_removals: int = 0

        for index, i in enumerate(emotes):

            if not isinstance(i, discord.Emoji):
                embed = discord.Embed(
                    title="That is not an custom emoji",
                    description=(
                        "You need to give me an custom discord emoji "
                        f"(Make sure the emoji that you give is actually in your server)\nYou passed in : {i}"
                    ),
                )
                await ctx.send(embed=embed)
                continue

            # For security reasons, we need to check if the emoji origin's is the same as ctx.guild
            if not i.guild.id == ctx.guild.id:
                embed = discord.Embed(
                    title="That is not an emoji from this server",
                    description="You need to give me an emoji that is actually in your server!",
                )
                await ctx.send(embed=embed)
                continue

            embed = discord.Embed(
                title=f"Removed {i.name}",
                description="Successfully removed the emoji from the server",
            )
            embed.set_footer(
                text=f"{index + 1} of {len(emotes)} to remove {'' if not (index + 1) == len(emotes) else '(over)'}"
            )

            successful_removals += 1
            await ctx.send(embed=embed)

        await self.bot.tools.increment_usage(
            ctx,
            TableType.rubric,
            successful_removals,
        )


def setup(bot):
    bot.add_cog(Remove(bot))
