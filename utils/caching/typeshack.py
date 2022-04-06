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
from typing import TYPE_CHECKING, Callable, TypeAlias, TypeVar

from discord import Message
from typing_extensions import Unpack

__all__: tuple[str, str] = ("PassIntoBase", "EmojiBot")

if TYPE_CHECKING:
    from ...main import EmojiBot
else:
    EmojiBot = TypeVar("EmojiBot")

PassIntoBase: TypeAlias = Callable[[Unpack[tuple[str, ...]]], Callable[[EmojiBot, Message], list[str]]]
