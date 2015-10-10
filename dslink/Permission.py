from enum import Enum


class Permission(Enum):
    NONE = "none",
    READ = "read",
    WRITE = "write",
    CONFIG = "config",
    NEVER = "never"
