from ..caching import CachingPod
from discord import Message
from discord.ext import commands
from enum import Enum
from typing import Literal


class _Sentinel(Enum):
    MISSING = object()


class PrefixHelper(CachingPod[int, list[str]]):
    async def __call__(
        self,
        bot: commands.Bot,
        message: Message,
        *,
        default_prefixes: Literal[_Sentinel.MISSING] | list[str] = _Sentinel.MISSING,
    ) -> list[str]:
        ...
        """
        Get the prefixes for the guild
        default_prefixes are extended to the existing prefixes (regardless of whether they are in the cache)

        Returns:
            list[str]: The prefixes for the guild with default_prefixes appended to the existing prefixes

        Example:
            >>> # Suppose the prefixes in cache were ["!", "?"]
            >>> await PrefixHelper(bot, message)
            ['!', '?']
            >>> # Suppose the prefixes in cache were ["!", "?"] and default_prefixes were ["$"]
            >>> await PrefixHelper(bot, message, default_prefixes=["$"])
            ['!', '?', '$']
            >>> # Suppose there were no prefixes in cache, but default_prefixes were ["pls"]
            >>> await PrefixHelper(bot, message, default_prefixes=["pls"])
            ['pls']
        """
        found: list | str = await self.get(message.guild.id, [])
        ret: list[str] = found if isinstance(found, list) else [found]
        ret.extend(
            default_prefixes
        ) if default_prefixes is not _Sentinel.MISSING else None
        return ret
