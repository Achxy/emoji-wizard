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
