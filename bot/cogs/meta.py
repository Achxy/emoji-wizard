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
# TODO: Complete the cog
from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    from core import EmojiBot


class Meta(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: "EmojiBot" = bot

    @commands.command()
    async def prefix(self, ctx: commands.Context) -> None:
        await ctx.send(str(self.bot.prefix))  # FIXME:


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Meta(bot))
