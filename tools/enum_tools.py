from enum import Enum


class CommandType(Enum):

    add = "cmd_add"
    enlarge = "cmd_enlarge"
    list = "cmd_list"
    ping = "cmd_ping"
    setprefix = "cmd_setprefix"
    rename = "cmd_rename"

    """
    I am aware of how using inspect.stack()[0][3] will completely eliminate the need for this
    But I chose this because this is an faster solution
    inspect.currentframe().f_back.f_code.co_name isn't an option either, it isn't stable with decorated functions
    Current implementation is the fastest way
    """


class EmojiRubric(Enum):
    """
    LHS contains the readable format
    RHS will logged into the database
    """

    addition = "add"
    enlargement = "enlarge"
    listed = "list"
    renamed = "rename"
