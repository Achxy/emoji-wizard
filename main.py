import os

import discord
from discord.ext import commands

from tools.database import Database


extensions = {
    "cogs": "⚙️",
}  # It's the emoji bot, what else would you expect?


bot: commands.Bot = commands.Bot(
    command_prefix=Database.get_prefix(debug=False),
    help_command=None,
    case_insensitive=True,
    allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True),
    intents=discord.Intents.all(),
)


@bot.event
async def on_ready():
    print(f"Successfully logged in as {bot.user}")


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


bot.run(os.getenv("DISCORD_TOKEN"))
