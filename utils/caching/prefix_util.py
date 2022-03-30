from .cache import AbstractBaseCache
import asyncpg, os


class PrefixHelper(AbstractBaseCache):
    def __call__(self, bot, message) -> list[str]:
        return ["!"]
