from asyncpg import Pool
from disnake.ext import commands
import time


class Database:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.pool: Pool = bot.db
        self._cached_prefixes: dict = {}

    async def confirm_tables(self):
        await self.pool.execute(
            """
            CREATE TABLE IF NOT EXISTS prefixes (
                guild_id bigint NOT NULL,
                prefix text NOT NULL,
                CONSTRAINT prefixes_pkey PRIMARY KEY (guild_id)
            );
            """
        )

    async def populate_cache(self) -> None:
        self._cached_prefixes = {}
        for record in await self.pool.fetch("SELECT * FROM prefixes"):
            self._cached_prefixes[record["guild_id"]] = record["prefix"]
        print(
            f"Successfully populated prefix cache, {len(self._cached_prefixes)} guilds cached"
        )

    @staticmethod
    def get_prefix(default_prefix, debug=False):
        def inner_get_prefix(bot, message):
            if not message.guild or message.guild.id not in bot.tools._cached_prefixes:
                return commands.when_mentioned_or(default_prefix)(bot, message)
            return commands.when_mentioned_or(
                bot.tools._cached_prefixes[message.guild.id]
            )(bot, message)

        return inner_get_prefix

    async def set_prefix(self, guild_id, new_prefix):
        await self.pool.execute(
            "INSERT INTO prefixes (guild_id, prefix) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET prefix = $2",
            guild_id,
            new_prefix,
        )
        self._cached_prefixes[guild_id] = new_prefix
