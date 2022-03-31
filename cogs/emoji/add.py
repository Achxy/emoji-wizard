from typing import Callable

import discord
from discord import PartialEmoji
from discord.ext import commands

from tools.bot_tools import animated_vacancy, page_index, static_vacancy


class Add(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO: Add more features and error handling to this.
    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def add(self, ctx, *emojis: PartialEmoji | str):

        footer_enumer: Callable[[int], str] = page_index("add", len(emojis))
        # Instead of making multiple function calls, we we will store vacancy as a variable
        # then decrement it as we move along
        var_static_vac = static_vacancy(ctx.guild)
        var_animated_vac = animated_vacancy(ctx.guild)

        for index, each_emoji in enumerate(emojis):

            if not isinstance(each_emoji, discord.PartialEmoji):
                embed = discord.Embed(
                    title="That is not an custom emoji",
                    description=f"You need to give me an custom discord emoji!\nYou passed in : {each_emoji}",
                )
                await ctx.send(embed=embed)
                continue

            elif (each_emoji.animated and var_animated_vac <= 0) or (
                not each_emoji.animated and var_static_vac <= 0
            ):
                embed = discord.Embed(
                    title="There are no more vacancy",
                    description="That emoji could not be added to the server because the emoji limit has been reached",
                )
                await ctx.send(embed=embed)
                continue

            # All working, add the emoji to the guild.
            try:
                added_emoji = await ctx.guild.create_custom_emoji(
                    name=each_emoji.name,
                    image=await each_emoji.read(),
                    reason=f"This emoji was added by {ctx.author} ({ctx.author.id})",
                )
            except Exception:
                # TODO: Make an better error handling in this case,
                # For now we'll continue in the loop
                continue
            else:
                # Success
                # Display the success message.
                embed = discord.Embed(
                    title=f"Successfully added {added_emoji.name}",
                    description=f"Successfully added {added_emoji} to the guild.",
                )
                embed.set_footer(text=footer_enumer(index))
                await ctx.send(embed=embed)

                # Decrement the vacancy
                if each_emoji.animated:
                    var_animated_vac -= 1
                else:
                    var_static_vac -= 1


def setup(bot):
    bot.add_cog(Add(bot))
