from enum import Enum

__all__ = ("TableType",)


class TableType(Enum):
    command = "usage"
    rubric = "emoji_rubric"
