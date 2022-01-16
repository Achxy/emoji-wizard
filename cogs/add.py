import discord
from discord.ext import commands


class add_(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO: Add more features and error handling to this.
    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def add(self, ctx, *emojis: discord.PartialEmoji):
        for each_emoji in emojis:
            await ctx.guild.create_custom_emoji(
                name=each_emoji.name,
                image=await each_emoji.read(),
                reason=f"This emoji was added by {ctx.author} ({ctx.author.id})",
            )


def setup(bot):
    bot.add_cog(add_(bot))
