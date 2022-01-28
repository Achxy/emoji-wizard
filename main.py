import discord
import os
import asyncpg
from discord.ext import commands, tasks
from database_tools import confirm_tables, get_usage_of
from bot_tools import get_default_prefix


DEFAULT_PREFIX = get_default_prefix()

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


initial_ext = list()
bot = commands.Bot(command_prefix=get_prefix, help_command=None, case_insensitive=True)

MIN_DELAY_OF_RPC = 25  # The use of this is mentioned under the docs of update_presence
bot._prev = None
bot._count = MIN_DELAY_OF_RPC


async def create_db_pool():
    bot.db = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    print("Successfully connected to the database")
    await confirm_tables(bot.db)


@bot.event
async def on_ready():
    print(f"Successfully logged in as {bot.user}")
    bot.usage_cache = await get_usage_of(bot.db, "global")
    if not update_presence.is_running():
        await bot.wait_until_ready()
        update_presence.start()


@tasks.loop(seconds=1)
async def update_presence():
    """
    We are interested in having overall command usage as the bot's rpc
    And this value being reflected in the rpc instantaneously after command usage is satisfactory
    If there are multiple changes in minimal duration of time then the rpc should not spam requests to the discord api
    here we will enforce our own limit to prevent such an occurence. This limit (in seconds) is dictated by MIN_DELAY_OF_RPC

    Albeit the database can handle multiple requests in a second (in terms of resources)
    We will not be checking the db every seconds because it is bad from a design perspective
    Instead we will be caching this under bot.prev_cache and inheritents of commands.Cog will manipulate this value
    Such way requests to the database can be kept to an minimum and be performant
    """
    #print(f"{bot._count = }, {bot._prev = }, {bot.usage_cache = }") # If you need to debug
    if (
        MIN_DELAY_OF_RPC > bot._count
    ):  # We don't really need to increment _count if it's already higher than MIN_DELAY_OF_RPC
        bot._count += 1
    if bot._prev == bot.usage_cache or MIN_DELAY_OF_RPC > bot._count:
        return
    bot._prev = bot.usage_cache
    bot._count = 0
    """
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.competing,
            name=f"worked with {bot.usage_cache}+ emotes",
        )
    )
    """
    # Uncomment the above code for the "competing in" status (and then comment the below code)
    await bot.change_presence(
        activity=discord.Game(name=f"worked with {bot.usage_cache}+ emotes")
    )


# To get all the .py files form the cogs folder
print("            -           ")
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        print(f"Adding {filename} from cogs...")
        initial_ext.append(f"cogs.{filename[:-3]}")


if __name__ == "__main__":
    for ext in initial_ext:
        bot.load_extension(ext)


bot.loop.run_until_complete(create_db_pool())
bot.run(os.getenv("DISCORD_TOKEN"))
