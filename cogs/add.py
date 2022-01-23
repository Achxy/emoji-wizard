import discord
import typing
from discord.ext import commands
from bot_tools import static_vacancy, animated_vacancy

class add_(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO: Add more features and error handling to this.
    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def add(self, ctx, *emojis: typing.Union[discord.PartialEmoji, str]):
        for index, each_emoji in enumerate(emojis):

            if static_vacancy(ctx.guild) == 0 and animated_vacancy(ctx.guild) == 0:
                # Send a message indicating that the guild cannot accept any more emotes
                # If this condition is hit then we want to terminate the function definition
                embed=discord.Embed(title="The guild is absolutely full", description="Your guild is full of emotes, it cannot accept any more of either static or animated emotes, please remove some emotes before trying again")
                await ctx.send(embed=embed)
                # End the function definiton
                return

            if isinstance(each_emoji, str):
                # To not process anything further if the user has given us an non-custom emoji.
                embed = discord.Embed(
                    title="That is not a custom emote",
                    description=f"{each_emoji} is not an custom emote and thus cannot be added to your guild",
                )
                embed.set_footer(
                    text=f"{index + 1} of {len(emojis)} to add {'' if not (index + 1) == len(emojis) else '(over)'}"
                )
                await ctx.send(embed=embed)
                continue
            
            if not each_emoji.animated and static_vacancy(ctx.guild) == 0:
                # Send a message indicating that the guild cannot accept any more static emotes
                embed=discord.Embed(title="Guild cannot accept any more of that", description=f"The guild cannot accept any more static emotes (perhaps add some animated emotes now) as such **{each_emoji.name}** was not added to the guild")
                embed.set_footer(
                    text=f"{index + 1} of {len(emojis)} to add {'' if not (index + 1) == len(emojis) else '(over)'}"
                )
                await ctx.send(embed=embed)
                continue

            if each_emoji.animated and animated_vacancy(ctx.guild) == 0:
                # Send a message indicating that the guild cannot accept any more animated emotes
                embed=discord.Embed(title="Guild cannot accept any more of that", description=f"The guild cannot accept any more animated emotes (perhaps add some static emotes now) as such **{each_emoji.name}** was not added to the guild")
                embed.set_footer(
                    text=f"{index + 1} of {len(emojis)} to add {'' if not (index + 1) == len(emojis) else '(over)'}"
                )
                await ctx.send(embed=embed)
                continue
            

            # All working, add the emoji to the guild.
            added_emoji = await ctx.guild.create_custom_emoji(
                name=each_emoji.name,
                image=await each_emoji.read(),
                reason=f"This emoji was added by {ctx.author} ({ctx.author.id})",
            )
            # Display the success message.
            embed = discord.Embed(
                title=f"Successfully added {added_emoji.name}",
                description=f"Successfully added {added_emoji} to the guild.",
            )
            embed.set_footer(
                text=f"{index + 1} of {len(emojis)} to add {'' if not (index + 1) == len(emojis) else '(over)'}"
            )
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(add_(bot))
