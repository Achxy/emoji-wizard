import discord
from discord.ext import commands
from tools.bot_tools import seperate_chunks


class list(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def cmd_list(self, ctx):
        """
        Send each emoji in the guild as a chunk of 10
        """

        count = 0
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
    bot.add_cog(list(bot))
