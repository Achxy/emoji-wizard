import disnake as discord
from disnake import Emoji
from disnake.ext import commands
from typing import Callable
from tools.bot_tools import page_index


class Remove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def remove(self, ctx, *emotes: Emoji | str):

        successful_removals: int = 0
        footer_enumer: Callable[[int], str] = page_index("remove", len(emotes))

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
            embed.set_footer(text=footer_enumer(index))

            successful_removals += 1
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Remove(bot))
