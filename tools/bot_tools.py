"""
EmojiWizard is a project licensed under GNU Affero General Public License.
Copyright (C) 2022-present  Achxy

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from typing import Callable, Generator, Sequence

import discord

__all__ = (
    "static_vacancy",
    "animated_vacancy",
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


def seperate_chunks(
    sequential_data: Sequence, into: int
) -> Generator[Sequence, None, None]:
    """
    This function takes a list and a number of chunks as arguments
    Returns a list of chunks of the list
    """
    for i in range(0, len(sequential_data), into):
        yield sequential_data[i : i + into]


def page_index(name: str, page_count: int) -> Callable:
    """
    This function takes a name and a page count as arguments
    Returns a function object
    """

    def pg(index: int) -> str:
        return f"{index + 1} of {page_count} to {name} {'' if not (index + 1) == page_count else '(over)'}"

    return pg
