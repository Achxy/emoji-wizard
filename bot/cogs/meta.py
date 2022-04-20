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
# XXX Incomplete

from discord.ext import commands
from discord.ext.commands import Context
from typeshack import EmojiBot


class Meta(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: EmojiBot = bot

    @commands.group()
    async def prefix(self, ctx: Context) -> None:
        """
        Manage the prefixes for the guild.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @prefix.command()
    async def set(self, ctx: commands.Context, prefix: str) -> None:
        await ctx.send("Hey")
        await self.bot.prefix.append(ctx.guild.id, prefix)
        await ctx.send(f"Successfully set the prefix to `{prefix}`")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Meta(bot))
