import disnake as discord
from disnake import PartialEmoji
from typing import Callable
from disnake.ext import commands
from tools.bot_tools import static_vacancy, animated_vacancy, page_index


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
            # Case 1: The guild cannot accept any more of any emotes
            # Case 2: The emote is an str
            # Case 3: The guild cannot accept any more of static emotes but can accept animated
            # Case 4: The guild cannot accept any more of animated emotes but can accept static
            # Case 5: The guild can accept both static and animated emotes (working!)
            # Now, we could combine them to have a bit less of repetition but I wanted custom messages for each

            if var_animated_vac == 0 and var_static_vac == 0:
                # Send a message indicating that the guild cannot accept any more emotes
                # If this condition is hit then we want to terminate the function definition
                embed = discord.Embed(
                    title="The guild is absolutely full",
                    description=(
                        "Your guild is full of emotes, "
                        "it cannot accept any more of either static or animated emotes, "
                        "please remove some emotes before trying again"
                    ),
                )
                await ctx.send(embed=embed)
                # End the function definiton
                return

            if isinstance(each_emoji, str):
                # To not process anything further if the user has given us an non-custom emoji.
                embed = discord.Embed(
                    title="That is not a custom emote",
                    description=f"{each_emoji} is not an custom emote and thus cannot be added to your guild",
                )
                embed.set_footer(text=footer_enumer(index))
                await ctx.send(embed=embed)
                continue

            if not each_emoji.animated and var_static_vac == 0:
                # Send a message indicating that the guild cannot accept any more static emotes
                embed = discord.Embed(
                    title="Guild cannot accept any more of that",
                    description=(
                        "The guild cannot accept any more static emotes "
                        "(perhaps add some animated emotes now) as such "
                        f"**{each_emoji.name}** was not added to the guild"
                    ),
                )
                embed.set_footer(text=footer_enumer(index))
                await ctx.send(embed=embed)
                continue

            if each_emoji.animated and var_animated_vac == 0:
                # Send a message indicating that the guild cannot accept any more animated emotes
                embed = discord.Embed(
                    title="Guild cannot accept any more of that",
                    description=(
                        "The guild cannot accept any more animated emotes (perhaps add some static emotes now) "
                        f"as such **{each_emoji.name}** was not added to the guild"
                    ),
                )
                embed.set_footer(text=footer_enumer(index))
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
