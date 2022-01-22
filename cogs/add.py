import discord
import typing
from discord.ext import commands


class add_(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO: Add more features and error handling to this.
    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def add(self, ctx, *emojis: typing.Union[discord.PartialEmoji, str]):
        for each_emoji in emojis:

            if isinstance(each_emoji, str):
                embed = discord.Embed(
                    title="That is not a custom emote",
                    description=f"{each_emoji} is not an custom emote and thus cannot be added to your guild",
                )
                await ctx.send(embed=embed)
                continue

            added_emoji = await ctx.guild.create_custom_emoji(
                name=each_emoji.name,
                image=await each_emoji.read(),
                reason=f"This emoji was added by {ctx.author} ({ctx.author.id})",
            )
            embed = discord.Embed(
                title=f"Successfully added {added_emoji.name}",
                description=f"Successfully added {added_emoji} to the guild.",
            )
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(add_(bot))
