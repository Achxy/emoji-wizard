import disnake as discord
import ast
import inspect
import re
from typing import Callable, Generator, Sequence

__all__ = (
    "static_vacancy",
    "animated_vacancy",
    "get_mobile",
    "seperate_chunks",
    "page_index",
)


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


def get_mobile() -> Callable:
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

    def source(o: Callable) -> str:
        s: list = inspect.getsource(o).split("\n")
        indent: int = len(s[0]) - len(s[0].lstrip())

        return "\n".join(i[indent:] for i in s)

    source_: str = source(discord.gateway.DiscordWebSocket.identify)
    patched: str = re.sub(
        r'([\'"]\$browser[\'"]:\s?[\'"]).+([\'"])',
        r"\1Discord Android\2",
        source_,
    )

    loc: dict = {}
    exec(compile(ast.parse(patched), "<string>", "exec"), discord.gateway.__dict__, loc)
    return loc["identify"]


def seperate_chunks(l: Sequence, into: int) -> Generator[Sequence, None, None]:
    """
    This function takes a list and a number of chunks as arguments
    Returns a list of chunks of the list
    """
    for i in range(0, len(l), into):
        yield l[i : i + into]


def page_index(name: str, page_count: int) -> Callable:
    """
    This function takes a name and a page count as arguments
    Returns a function object
    """

    def pg(index: int) -> str:
        return f"{index + 1} of {page_count} to {name} {'' if not (index + 1) == page_count else '(over)'}"

    return pg
