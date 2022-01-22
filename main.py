import discord
import os
import json
from discord.ext import commands


try:
    with open("config.json", "r") as r:
        # This is to check if an config.json file exists
        # And the user has not entered anything weird onto the json file.
        _ = json.load(r)
        # If the doesn't raise any exceptions then that means the json file is valid
except Exception as err:
    # Invalid json or config.json doesn't exist

    default_json_config = """{
    "default_prefix": "?",
    "status": "idle",
    "rpc_type": "playing",
    "rpc_text": "with Emojis!"
}"""

    with open("config.json", "w+") as w:
        w.write(default_json_config)

    print(f"Caught {err} with json file, it has been reset to default")


# Parsing out the user preferences stored in config.json
# TODO: Make complete use of the json file, for now it only works with prefix

with open("config.json", "r") as preference:
    preference = json.load(preference)

bot_prefix = preference["default_prefix"]

initial_ext = list()
bot = commands.Bot(command_prefix=bot_prefix, help_command=None)


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
