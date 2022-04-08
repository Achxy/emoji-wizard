from __future__ import annotations
from typing import TYPE_CHECKING
from asyncpg import Record


def textualize(rec: list[Record], join="") -> str:
    return join.join(map(lambda x: str(x), rec))
