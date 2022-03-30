import os

__all__: tuple[str] = ("findenv",)


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
