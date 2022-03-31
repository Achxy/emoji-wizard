import os

import asyncpg

from .cache import BaseCache

_MISSING = object()


class PrefixHelper(BaseCache):
    def __call__(self, bot, message) -> list[str]:

        return (
            self.get(message.guild.id if message.guild else _MISSING, []) + self.default
        )
