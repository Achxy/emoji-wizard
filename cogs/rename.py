import discord
import typing
from discord.ext import commands


class rename_(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def rename(self, ctx, *emoji_and_name: typing.Union[discord.Emoji, str]):
        """
        Albeit variadic accepts many, we only accept 2 and raise issues if there are more than 2 args
        The two args can be in any order, one of which is discord.Emoji and the one is a str instance

        Since bot only checks for manage_emojis perm in current guild but acts upon emojis in the bot's guild emoji pool
        we need to confirm that the emoji we are acting upon matches ctx.guild to prevent any attackers
        """
        # FIXME: Replace placeholder "prefix" with actual prefix
        # Check if the argument count is 2 or not
        if len(emoji_and_name) > 2:
            embed = discord.Embed(
                title="That command only takes 2 arguments",
                description=f"`rename` command only takes 2 arguments but you have given **{len(emoji_and_name)}**.\nThe syntax for `rename` is : `prefixrename <emoji> <name>`",
            )
            await ctx.send(embed=embed)
            return
        if len(emoji_and_name) < 2:
            embed = discord.Embed(
                title="That command at least takes 2 arguments",
                description=f"`rename` command at least takes 2 arguments but you have only given **{len(emoji_and_name)}**.\nThe syntax for `rename` is : `prefixrename <emoji> <name>`",
            )
            await ctx.send(embed=embed)
            return

        emoji = None
        name = None

        for i in emoji_and_name:
            if isinstance(i, discord.Emoji):
                emoji = i
            else:
                name = i

        if emoji is None or name is None:
            embed = discord.Embed(
                title="Bad arguments",
                description="You need to give me exactly one emoji (that is actually in your guild) and exactly one name",
            )
            await ctx.send(embed=embed)

        # For security reasons we need to check the orgin of the emoji (guild)
        # Matches that of context's guild
        if not emoji.guild_id == ctx.guild.id:
            embed = discord.Embed(
                title="Gimme a emoji that is actually in your guild",
                description="That emoji isn't actually in your guild.",
            )
            await ctx.send(embed=embed)
            return

        # TODO: Better error handling
        # Probably will fix it in an anothor PR
        try:
            await emoji.edit(
                name=name, reason=f"Edited emoji by {ctx.author} ({ctx.author.id})"
            )
        except:
            pass


def setup(bot):
    bot.add_cog(rename_(bot))
