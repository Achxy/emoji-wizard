from enum import Enum


class CommandType(Enum):
    """
    Enum for the different types of commands.
    and their corresponding usage stored in the database.
    """

    add = "cmd_add"
    enlarge = "cmd_enlarge"
    list = "cmd_list"
    ping = "cmd_ping"
    setprefix = "cmd_setprefix"
    help = "cmd_help"
    remove_all = "cmd_remove_all"
    remove = "cmd_remove"
    rename = "cmd_rename"
    source = "cmd_source"
    enable = "cmd_enable"
    disable = "cmd_disable"
    ignore = "cmd_ignore"
    unignore = "cmd_unignore"


class EmojiRubric(Enum):

    additon = "rubric_add"
    enlargement = "rubric_enlarge"
    list = "rubric_list"
    removal = "rubric_remove"
    rename = "rubric_rename"
