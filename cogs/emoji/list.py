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
from discord.ext import commands

from tools.bot_tools import seperate_chunks


class ListEmojis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=[
            "list",
        ]
    )
    async def list_emoji(self, ctx):
        """
        Send each emoji in the guild as a chunk of 10
        """

        count: int = 0
        for each_chunk in seperate_chunks(ctx.guild.emojis, 10):
            msg = ""
            for each_emoji in each_chunk:
                count += 1
                if each_emoji.available:
                    msg += f"{count}. {each_emoji} -- `{each_emoji}`\n"
                else:
                    msg += f"{count}. ~~{each_emoji}~~ -- `{each_emoji}` **(unavailable)**\n"
            await ctx.send(msg)


def setup(bot):
    bot.add_cog(ListEmojis(bot))
