import asyncpg


class Cache:
    """
    IMPORTANT NOTE : Incrementing values in cache can write those values to the database
    This structure is to prevent repetitive code and to make caching and registering be done in single place
    This class can write to the database

    The purpose of this is to make the bot send as little requests as possible to database
    Which consequentially will make the bot work faster (as there isn't anything to fetch)
    To achieve this, bot will internally increment usage stat before registering them to database
    And will fetch the cache vars instead of fetching the database later on.

    To achieve cleaner code, commands can be decorated with @Cache.command(...)
    with command type as sole argument to register command usage

    """

    def __init__(self, pool: asyncpg.pool.Pool) -> None:
        """
        To work with the database, we need to accept asyncpg.pool.Pool object
        """
        self.pool = pool

    def command(self, type_of_command: str):
        def wrapper(function):
            def inner_wrapper(*args, **kwargs):
                return function(*args, **kwargs)

            return inner_wrapper

        return wrapper
