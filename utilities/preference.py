import discord
import functools
from discord.ext import commands


class Preference(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_usable(self, func=None):
        """
        This is a decorator that checks for preference in context
        works regardless of whether this is used with a instance or not
        """
        func = self if func is None else func
        # It may look like this line of code can be replaced with a
        # @classmethod or @staticmethod decorator but it cannot be,
        # The reason for it is because doing that will loose us the self
        # which we need.

        @functools.wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            if await self.bot.tools.is_preferred_channel(ctx.guild.id, ctx.channel.id):
                return await func(self, ctx, *args, **kwargs)
            raise RuntimeError("This command can only be used in preferred channels")

        return wrapper


def setup(bot):
    bot.add_cog(Preference(bot))
