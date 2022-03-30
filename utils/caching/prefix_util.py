from .cache import AbstractBaseCache
import asyncpg, os

_MISSING = object()


class PrefixHelper(AbstractBaseCache):
    def __call__(self, bot, message) -> list[str]:

        return (
            self.get(message.guild.id if message.guild else _MISSING, []) + self.default
        )
