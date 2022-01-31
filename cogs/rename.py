import discord
import typing
from discord.ext import commands
from database_tools import get_prefix_for_guild


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

        cmd_type = "cmd_rename"

        # Check if the argument count is 2 or not
        if len(emoji_and_name) > 2:
            prefix = await get_prefix_for_guild(self.bot.db, ctx.guild)
            embed = discord.Embed(
                title="That command only takes 2 arguments",
                description=f"`rename` command only takes 2 arguments but you have given **{len(emoji_and_name)}**.\nThe syntax for `rename` is : \n\n`{prefix}rename <emoji> <name>`",
            )
            await ctx.send(embed=embed)
            return
        if len(emoji_and_name) < 2:
            prefix = await get_prefix_for_guild(self.bot.db, ctx.guild)
            embed = discord.Embed(
                title="That command at least takes 2 arguments",
                description=f"`rename` command at least takes 2 arguments but you have only given **{len(emoji_and_name)}**.\nThe syntax for `rename` is : \n\n`{prefix}rename <emoji> <name>`",
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
                description="You need to give me exactly one emoji (__that is actually in your guild__) and exactly one name",
            )
            await ctx.send(embed=embed)
            return

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
            before_name = emoji.name
            new_emoji = await emoji.edit(
                name=name, reason=f"Edited emoji by {ctx.author} ({ctx.author.id})"
            )
            after_name = new_emoji.name
        except Exception:
            pass
        else:
            # Success
            embed = discord.Embed(
                title="Success!",
                description=f"Successfully renamed {new_emoji} from **{before_name}** to **{after_name}**",
            )
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(rename_(bot))
