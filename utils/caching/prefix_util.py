from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Message

from .cache import BaseCache

if TYPE_CHECKING:
    from ...main import EmojiBot

_MISSING = object()


class PrefixHelper(BaseCache):
    def __call__(self, bot: EmojiBot, message: Message) -> list[str]:
        ret = self.get(message.guild.id if message.guild else _MISSING, [])
        ret = ret if isinstance(ret, list) else [ret]

        return ret + self.default
