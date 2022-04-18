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
from typing import Final

from discord import AllowedMentions, Intents


__all__: Final[tuple[str, ...]] = (
    "DEFAULT_PREFIX",
    "INTENTS",
    "ALLOWED_MENTIONS",
    "LOGGING_FORMAT",
)


DEFAULT_PREFIX: Final[tuple[str, ...]] = ("!", "wiz ")
INTENTS: Final[Intents] = Intents(
    guilds=True,
    members=True,
    bans=False,
    emojis_and_stickers=True,
    integrations=False,
    webhooks=False,
    invites=False,
    voice_states=False,
    presences=False,
    messages=True,
    reactions=True,
    typing=False,
    message_content=True,
    guild_scheduled_events=False,
)
ALLOWED_MENTIONS: Final[AllowedMentions] = AllowedMentions.none()
ALLOWED_MENTIONS.replied_user = True

LOGGING_FORMAT: Final[str] = "[%(levelname)s] [%(asctime)s] %(message)s"
