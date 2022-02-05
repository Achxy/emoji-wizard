import discord
import os
import asyncpg
from discord.ext import commands
from tools.database_tools import DatabaseTools
from tools.bot_tools import get_mobile


discord.gateway.DiscordWebSocket.identify = (
    get_mobile()
)  # Remove this line if bot isn't working, experimental thing
DEFAULT_PREFIX: str = "?"

# Get custom prefix for the guild
# Handle if not used in guild
async def get_prefix(bot, message):
    if not message.guild:
        return commands.when_mentioned_or(DEFAULT_PREFIX)(bot, message)

    # Actually in a guild
    query = "SELECT prefix FROM guilds WHERE guild_id = $1"
    prefix = await bot.db.fetch(query, message.guild.id)

    if len(prefix) == 0:
        query = "INSERT INTO guilds (guild_id, prefix) VALUES ($1, $2)"
        await bot.db.execute(query, message.guild.id, DEFAULT_PREFIX)
        prefix = DEFAULT_PREFIX

    else:
        prefix = prefix[0].get("prefix")
    return commands.when_mentioned_or(prefix)(bot, message)


bot = commands.Bot(command_prefix=get_prefix, help_command=None, case_insensitive=True)


async def create_db_pool():
    bot.db = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    print("Successfully connected to the database")
    bot.tools = DatabaseTools(bot)
    await bot.tools.confirm_tables()


@bot.event
async def on_ready():
    print(f"Successfully logged in as {bot.user}")


# Get all the python files from the cogs folder
# and add them as cogs with bot.load_extension
print("            -           ")  # This is just for the formatting
for filename in os.listdir("./cogs"):
    # Check if the file is a python file
    if filename.endswith(".py"):
        # Print the filename
        print(f"Adding {filename} from cogs...", end="")
        # Load the cog after stripping the .py
        bot.load_extension(f"cogs.{filename[:-3]}")
        # Give the user a nice 'Done' message to make them happy
        print("Done")


bot.loop.run_until_complete(create_db_pool())
bot.run(os.getenv("DISCORD_TOKEN"))
