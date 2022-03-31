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
from discord.ext import commands
from discord.ui import Button, View


class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def invite(self, ctx):
        """
        Sends a link to invite the bot to your server
        """
        link = (
            "https://discord.com/api/oauth2/authorize"
            f"?client_id={self.bot.user.id}&permissions=140660493376&scope=bot"
        )

        # Embed :
        embed = discord.Embed(
            title=f"Invite {self.bot.user.name} to your server!",
            url=link,
            description=f"Use this [link]({link}) to invite me to your server!",
        )
        embed.set_thumbnail(
            url=self.bot.user.avatar.url
            if self.bot.user.avatar is not None
            else self.bot.user.default_avatar.url
        )
        embed.set_footer(
            text=f"{self.bot.user.name} is in {len(self.bot.guilds)} guilds :D"
        )

        # View :
        invite_button = Button(label="Invite me!", url=link)
        view = View()
        view.add_item(invite_button)

        await ctx.send(embed=embed, view=view)


def setup(bot):
    bot.add_cog(Invite(bot))
