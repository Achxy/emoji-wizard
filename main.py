import disnake as discord
import os
import asyncpg
from disnake.ext import commands
from tools.bot_tools import get_mobile
from tools.database import Database


discord.gateway.DiscordWebSocket.identify = (
    get_mobile()
)  # Remove this line if you don't want mobile status
DEFAULT_PREFIX = "?"
extensions = {
    "cogs": "⚙️",
}  # It's the emoji bot, what else would you expect?


bot: commands.Bot = commands.Bot(
    command_prefix=Database.get_prefix(DEFAULT_PREFIX, debug=False),
    help_command=None,
    case_insensitive=True,
)


async def create_db_pool():
    bot.db = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    print("Successfully connected to the database")
    bot.tools = Database(bot)
    await bot.tools.confirm_tables()


@bot.event
async def on_ready():
    print(f"Successfully logged in as {bot.user}")
    await bot.tools.populate_cache()


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
