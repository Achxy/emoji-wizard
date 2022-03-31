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
from discord import PartialEmoji
from discord.ext import commands

from tools.bot_tools import page_index


class Enlarge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def enlarge(self, ctx, *emotes: PartialEmoji | str):

        footer_enumer: Callable[[int], str] = page_index("enlarge", len(emotes))

        for index, i in enumerate(emotes):

            if not isinstance(i, discord.PartialEmoji):
                embed = discord.Embed(
                    title="That is not an custom emoji",
                    description=f"You need to give me an custom discord emoji!\nYou passed in : {i}",
                )
                await ctx.send(embed=embed)
                continue

            embed = discord.Embed(title=f"Enlarged view of {i.name}")
            embed.set_image(url=i.url)
            embed.set_footer(text=footer_enumer(index))

            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Enlarge(bot))
