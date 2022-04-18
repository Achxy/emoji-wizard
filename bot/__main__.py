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
import asyncio
import logging

import asyncpg
import tools
from core import EmojiBot
from options import ALLOWED_MENTIONS, DEFAULT_PREFIX, INTENTS, LOGGING_FORMAT

logging.basicConfig(
    level=logging.INFO,
    format=LOGGING_FORMAT,
)


async def main() -> None:
    """
    Instantiates `EmojiBot` and starts it.
    This is the main entry point for the bot.
    """
    bot: EmojiBot = EmojiBot(
        default_prefix=DEFAULT_PREFIX,
        allowed_mentions=ALLOWED_MENTIONS,
        intents=INTENTS,
        pool=await asyncpg.create_pool(tools.findenv("DATABASE_URL")),
    )
    await bot.start(tools.findenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())
