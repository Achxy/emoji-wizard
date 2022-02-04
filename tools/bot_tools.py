import discord
import ast
import inspect
import re
import json


def static_vacancy(guild: discord.guild.Guild) -> int:
    """
    This function takes guild object as sole argument
    Returns an integer reflecting count of additional static emotes the guild could potentially accept
    """
    return guild.emoji_limit - len([_ for _ in guild.emojis if not _.animated])


def animated_vacancy(guild: discord.guild.Guild) -> int:
    """
    This function takes guild object as sole argument
    Returns an integer reflecting count of additional animated emotes the guild could potentially accept
    """
    return guild.emoji_limit - len([_ for _ in guild.emojis if _.animated])


def reset_config_json(file="config.json"):
    """
    Overwrite config.json file with default values
    This is supposed to be called when when the content of the file is bad
    """
    with open(file, "w+") as fwp:
        default_json = '{"DEFAULT_PREFIX": "?"}'
        fwp.write(default_json)


def get_default_prefix(file="config.json", key="DEFAULT_PREFIX"):
    """
    Get the value stored in key arg in file arg
    Creates the data with default prefix if it does not exists or if the json data is bad

    You may be wondering why such an json file exists when we are already attached to an actual database
    The reason is that database_tools references main for getting the default prefix and
    the main file obviously imported the database tools which lead to an circular import
    to fix this, I used to store default prefix in an file that is outside

    To make it as easy as possible for someone to host this bot and set the default prefix they desire
    I have decided to store it in a json file 
    Custom prefixes are of course stored in the database
    """
    try:
        with open(file, "r") as fr:
            j = json.load(fr)
            return j[key]
    except Exception:
        reset_config_json(file=file)
        with open(file, "r") as fr:
            j = json.load(fr)
            return j[key]

def get_mobile():
    """
    This is unstable and may break your bot, but it is fun :D

    Takes no argument, returns function object
    Overwrite in place for discord.gateway.DiscordWebSocket.identify
    
    The Gateway's IDENTIFY packet contains a properties field, containing $os, $browser and $device fields.
    Discord uses that information to know when your phone client and only your phone client has connected to Discord,
    from there they send the extended presence object.
    The exact field that is checked is the $browser field. If it's set to Discord Android on desktop,
    the mobile indicator is is triggered by the desktop client. If it's set to Discord Client on mobile,
    the mobile indicator is not triggered by the mobile client.
    The specific values for the $os, $browser, and $device fields are can change from time to time.
    """


    def source(o):
        s = inspect.getsource(o).split("\n")
        indent = len(s[0]) - len(s[0].lstrip())

        return "\n".join(i[indent:] for i in s)

    source_ = source(discord.gateway.DiscordWebSocket.identify)
    patched = re.sub(
        r'([\'"]\$browser[\'"]:\s?[\'"]).+([\'"])',
        r"\1Discord Android\2",
        source_,
    )

    loc = {}
    exec(compile(ast.parse(patched), "<string>", "exec"), discord.gateway.__dict__, loc)
    return loc["identify"]


def seperate_chunks(l, into):
    """
    This function takes a list and a number of chunks as arguments
    Returns a list of chunks of the list
    """
    for i in range(0, len(l), into):
        yield l[i : i + into]
