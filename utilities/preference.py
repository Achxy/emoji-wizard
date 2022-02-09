import discord
import functools
from discord.ext import commands


class Preference(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_usable(func):
        @functools.wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            if await self.bot.tools.is_preferred_channel(ctx.guild.id, ctx.channel.id):
                return await func(self, ctx, *args, **kwargs)
            raise RuntimeError("This command can only be used in preferred channels")

        return wrapper


def setup(bot):
    bot.add_cog(Preference(bot))
