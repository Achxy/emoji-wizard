from asyncpg import Pool
from disnake.ext import commands


class Database:
    def __init__(self, pool) -> None:
        self.pool: Pool = pool
        self._cached_prefixes: dict = {}

    async def populate_cache(self) -> None:
        for record in await self.pool.fetch("SELECT * FROM prefixes"):
            self._cached_prefixes[record["guild_id"]] = record["prefix"]

    async def get_prefix(self, default_prefix):
        async def inner_get_prefix(bot, message):
            if not message.guild or message.guild.id not in self._cached_prefixes:
                return commands.when_mentioned_or(default_prefix)(bot, message)
            return commands.when_mentioned_or(self._cached_prefixes[message.guild.id])(
                bot, message
            )

        return inner_get_prefix

    async def set_prefix(self, guild_id, new_prefix):
        await self.pool.execute(
            "INSERT INTO prefixes (guild_id, prefix) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET prefix = $2",
            guild_id,
            new_prefix,
        )
        self._cached_prefixes[guild_id] = new_prefix
