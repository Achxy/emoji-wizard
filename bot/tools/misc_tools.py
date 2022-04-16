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
import os

from dotenv import load_dotenv

load_dotenv()

__all__: tuple[str, ...] = ("findenv", "load_query")


def findenv(key: str, /) -> str:
    """
    This function is similar in behavior to os.getenv()
    but instead of returning None, it raises an exception when the key is not found

    Args:
        key (str): The key to search for

    Raises:
        KeyError: When the key is not found

    Returns:
        str: The value associated with the key
    """
    # This is mostly just to make pyright happy
    ret = os.getenv(key)

    if ret is None:
        raise KeyError(
            (
                f"{key} not found in environment, "
                "consider making a .env file in the root of the directory "
                f"with the appropriate keys"
            )
        )
    return ret


def load_query(file_path: str) -> str:
    """
    Loads a query from a file

    Args:
        file_path (str): The path to the file

    Returns:
        str: The query
    """
    if not file_path.endswith(".sql"):
        raise ResourceWarning("Given file path does not end with .sql")

    with open(file_path, "r", encoding="UTF-8") as sql_query_file:
        return sql_query_file.read()
