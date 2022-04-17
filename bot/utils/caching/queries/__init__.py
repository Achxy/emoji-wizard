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

from pathlib import Path
from typing import Final

__all__: Final[tuple[str, ...]] = (
    "load_query",
    "CREATE_PREFIX_TABLE",
    "INSERT",
    "REMOVE",
    "REMOVE_ALL",
    "SELECT",
)


def load_query(file_path: str | Path) -> str:
    """
    Loads a query from a file

    Args:
        file_path (str): The path to the file

    Returns:
        str: The query
    """
    if not str(file_path).endswith(".sql"):
        raise ResourceWarning("Given file path does not end with .sql")

    with open(file_path, "r", encoding="UTF-8") as sql_query_file:
        return sql_query_file.read()


_PATH = Path(__file__).parent
CREATE_PREFIX_TABLE: Final[str] = load_query(_PATH / "create.sql")
INSERT: Final[str] = load_query(_PATH / "insert.sql")
REMOVE: Final[str] = load_query(_PATH / "remove.sql")
REMOVE_ALL: Final[str] = load_query(_PATH / "remove_all.sql")
SELECT: Final[str] = load_query(_PATH / "select.sql")
