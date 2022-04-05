from typing import TYPE_CHECKING, Callable, TypeAlias, TypeVar

from discord import Message
from typing_extensions import Unpack

if TYPE_CHECKING:
    from ...main import EmojiBot
else:
    EmojiBot = TypeVar("EmojiBot")

PassIntoBase: TypeAlias = Callable[
    [Unpack[tuple[str, ...]]], Callable[["EmojiBot", Message], list[str]]
]
