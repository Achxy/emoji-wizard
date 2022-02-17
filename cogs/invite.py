import disnake as discord
from disnake.ui import View, Button
from disnake.ext import commands
from helpers.context_patch import PatchedContext, EditInvokeContext


class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def invite(self, ctx: EditInvokeContext | PatchedContext):
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
