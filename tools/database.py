from discord.ext import commands
import time

DEFAULT_PREFIX = "?"


class Database:
    def __init__(self, bot) -> None:
        self.bot = bot

    async def confirm_tables(self):

        query = """
                CREATE TABLE IF NOT EXISTS prefixes (
                guild_id bigint NOT NULL,
                prefix text NOT NULL,
                CONSTRAINT prefixes_pkey PRIMARY KEY (guild_id)
                );
                """

        await self.bot.db.execute(query)

    @staticmethod
    def _debug(start_time: float, message: str, convert=1000):
        def check_point():
            print(message.format((time.perf_counter() - start_time) * convert))

        return check_point

    @staticmethod
    def get_prefix(default_prefix=DEFAULT_PREFIX, debug=False):
        def inner_get_prefix(bot, message):
            check_point = __class__._debug(
                time.perf_counter(), "Prefix lookup took {}ms"
            )
            if not message.guild:
                check_point() if debug else None
                return commands.when_mentioned_or(default_prefix)(bot, message)
            prefix = bot.db.fetch(
                "SELECT prefix FROM prefixes WHERE guild_id = $1", message.guild.id
            )
            r = commands.when_mentioned_or(
                *list(map(lambda x: x[0], prefix) if prefix else default_prefix)
            )(bot, message)
            check_point() if debug else None
            return r

        return inner_get_prefix

    async def set_prefix(self, guild_id: int, new_prefix: str):
        await self.bot.db.execute(
            "INSERT INTO prefixes (guild_id, prefix) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET prefix = $2",
            guild_id,
            new_prefix,
        )
