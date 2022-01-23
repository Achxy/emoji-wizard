import discord

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


def word_to_object(word: str):
    word = word.lower()

    if word == "online":
        return discord.Status.online
    
    elif word == "idle":
        return discord.Status.idle

    elif word == "dnd" or word == "do_not_disturb":
        return discord.Status.do_not_disturb