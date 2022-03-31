"""
EmojiWizard is a project licensed under GNU Affero General Public License.
Copyright (C) 2022-present  Achxy

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import discord
from discord import Emoji
from discord.ext import commands


class Rename(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def rename(self, ctx, *emoji_and_name: Emoji | str):
        """
        Albeit variadic accepts many, we only accept 2 and raise issues if there are more than 2 args
        The two args can be in any order, one of which is discord.Emoji and the one is a str instance

        Since bot only checks for manage_emojis perm in current guild but acts upon emojis in the bot's guild emoji pool
        we need to confirm that the emoji we are acting upon matches ctx.guild to prevent any attackers
        """

        # Check if the argument count is 2 or not
        # TODO: do not hardcode this but handle this in handlers.py
        if not len(emoji_and_name) == 2:
            embed = discord.Embed(
                title="That command only takes 2 arguments",
                description=f"`rename` command takes 2 arguments but you have given **{len(emoji_and_name)}**.\nThe syntax for `rename` is : \n\n`{ctx.prefix}rename <emoji> <name>`",
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
    bot.add_cog(Rename(bot))
