from enum import Enum


class Role(str, Enum):
    root = "ROOT"
    user = "USER"
    admin = "ADMIN"

class UserActions(str, Enum):
    logged_in = "LOGGED_IN"
