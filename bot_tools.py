import discord
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


def seperate_chunks(l, into):
    for i in range(0, len(l), into):
        yield l[i : i + into]
