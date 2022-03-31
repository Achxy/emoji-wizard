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
from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Message

from .cache import BaseCache

if TYPE_CHECKING:
    from ...main import EmojiBot

_MISSING = object()


class PrefixHelper(BaseCache):
    def __call__(self, bot: EmojiBot, message: Message) -> list[str]:
        ret = self.get(message.guild.id if message.guild else _MISSING, [])
        ret = ret if isinstance(ret, list) else [ret]

        return ret + self.default
