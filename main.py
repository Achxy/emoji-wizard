import discord
import os
import asyncpg
from discord.ext import commands

DEFAULT_PREFIX = "?"

initial_ext = list()
bot = commands.Bot(command_prefix=DEFAULT_PREFIX, help_command=None)


@bot.event
async def on_ready():
    print(f"Sucessfully logged in as {bot.user}")


# To get all the .py files form the cogs folder
print("            -           ")
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        print(f"Adding {filename} from cogs...")
        initial_ext.append(f"cogs.{filename[:-3]}")


if __name__ == "__main__":
    for ext in initial_ext:
        bot.load_extension(ext)


bot.run(os.getenv("DISCORD_TOKEN"))
