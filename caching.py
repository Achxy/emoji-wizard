class Cache:
    """
    IMPORTANT NOTE : Incrementing values in cache can write those values to the database
    This structure is to prevent repetitive code and to make caching and registering be done in single place
    This class can write to the database

    The purpose of this is to make the bot send as little requests as possible to database
    Which consequentially will make the bot work faster (as there isn't anything to fetch)
    To achieve this, bot will internally increment usage stat before registering them to database
    And will fetch the cache vars instead of fetching the database later on.

    Command usage and emoji usage rubric are cached seperately
    """
