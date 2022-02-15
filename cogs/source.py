import disnake as discord
import inspect
import os
from typing import Optional
from disnake.ext import commands
from tools.enum_tools import TableType


class Source(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def source(self, ctx, *, command: Optional[str] = None):
        """
        Displays my full source code or for a specific command.
        """
        source_url = "https://github.com/Achxy/emoji-wizard"
        branch = "main"
        if command is None:
            embed = discord.Embed(
                title="Emoji-wizard is an open source project!",
                description=f"You can find it's source code here : **{source_url}**",
            )
            await ctx.send(embed=embed)
            return

        if command == "help":
            src = type(self.bot.help_command)
            module = src.__module__
            filename = inspect.getsourcefile(src)

        else:
            obj = self.bot.get_command(command.replace(".", " "))
            if obj is None:
                return await ctx.send("Could not find command.")

            # since we found the command we're looking for, presumably anyway, let's
            # try to access the code itself
            src = obj.callback.__code__
            module = obj.callback.__module__
            filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)
        if not module.startswith("discord"):
            # not a built-in command
            location = os.path.relpath(filename).replace("\\", "/")
        else:
            location = module.replace(".", "/") + ".py"
            source_url = "https://github.com/Rapptz/discord.py"
            branch = "master"

        final_url = f"<{source_url}/blob/{branch}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>"
        await ctx.send(final_url)


def setup(bot):
    bot.add_cog(Source(bot))
