import disnake as discord
import os
import asyncpg
import time
from disnake.ext import commands
from tools.database_tools import DatabaseTools
from tools.enum_tools import TableType
from tools.caching import Cache
from tools.bot_tools import get_mobile, get_default_prefix
from tools.interim import Interim
from helpers.context_patch import PatchedContext


discord.gateway.DiscordWebSocket.identify = (
    get_mobile()
)  # Remove this line if bot isn't working, experimental thing
DEFAULT_PREFIX: str = get_default_prefix()
extensions = {
    "cogs": "⚙️",
    "utilities": "🚀",
}  # It's the emoji bot, what else would you expect?


# Get custom prefix for the guild
# Handle if not used in guild
async def get_prefix(bot: commands.Bot, message: discord.Message):
    if not message.guild:
        return commands.when_mentioned_or(DEFAULT_PREFIX)(bot, message)

    prefix = await bot.cache.get_prefix(
        TableType.guilds, message.guild.id, DEFAULT_PREFIX
    )

    return commands.when_mentioned_or(prefix)(bot, message)


bot: commands.Bot = commands.Bot(
    command_prefix=get_prefix, help_command=None, case_insensitive=True
)


async def create_db_pool():
    bot.db = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    print("Successfully connected to the database")
    bot.tools = DatabaseTools(bot)
    await bot.tools.confirm_tables()
    bot.cache = Cache(bot)
    bot.interim = Interim(bot)


@bot.event
async def on_ready():
    print(f"Successfully logged in as {bot.user}")
    _t0: float = time.perf_counter()
    for table in TableType:
        await bot.cache.populate_cache(table)
    _t1: float = time.perf_counter()
    print(f"Successfully populated cache in {_t1 - _t0}s (for {len(TableType)} tables)")


@bot.event
async def on_message(message: discord.Message):
    # Here we override the default on_message function
    # We will process commands from here but with our own context class
    ctx = await bot.get_context(message, cls=PatchedContext)
    await bot.invoke(ctx)


# Get all the python files from the cogs folder
# and add them as cogs with bot.load_extension
print("            -           ")  # This is just for the formatting
for ext in extensions:
    print(f"Getting extensions from {ext}", end=f"\n{'-' * 10}\n")
    for filename in os.listdir(f"./{ext}"):
        # Check if the file is a python file
        if filename.endswith(".py"):
            # Print the filename
            print(f"Adding {filename} from {ext} {extensions[ext]} ...", end="")
            # Load the cog after stripping the .py
            bot.load_extension(f"{ext}.{filename[:-3]}")
            # Give the user a nice 'Done' message to make them happy
            print("Done")
    print()


bot.loop.run_until_complete(create_db_pool())
bot.run(os.getenv("DISCORD_TOKEN"))
