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


"""
# Status to Online (The green one)
await client.change_presence(status=discord.Status.online)

# Status to Idle (The orange one)
await client.change_presence(status=discord.Status.idle)

# Status to Do not disturb (The red one)
await client.change_presence(status=discord.Status.dnd)


# Playing ____
await bot.change_presence(activity=discord.Game(name='Minecraft'))
# Streaming ____
await bot.change_presence(activity=discord.Streaming(name="Chess", url=twitch_url))
# Watching ____
await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Harry Potter"))
# Competing in ____
await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name="the House Cup"))
# Listening to ____
await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help"))

"""
def word_to_object(word: str):
    word = word.lower()

    if word == "online":
        return discord.Status.online
    
    elif word == "idle":
        return discord.Status.idle

    elif word == "dnd" or word == "do_not_disturb":
        return discord.Status.do_not_disturb