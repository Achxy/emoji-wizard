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
from typing import Callable

import discord
from discord import Emoji
from discord.ext import commands

from tools.bot_tools import page_index


class Remove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def remove(self, ctx, *emotes: Emoji | str):

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

            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Remove(bot))
