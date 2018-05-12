# coding=utf-8
from numbers import Number
from datetime import datetime

from .Util import base64_decode
from .six import string_types


TYPES = [
    "number",
    "int",
    "uint",
    "string",
    "bool",
    "enum",
    "binary",
    "map",
    "array",
    "dynamic"
]


class Value:
    def __init__(self):
        """
        Constructor for Value.
        """
        self.value = None
        self.type = None
        self.updated_at = None

    def set_type(self, t):
        """
        Set the type for this Value.
        :param t: Value type.
        :return: True on success.
        """
        if self.is_enum(t):
            pass
        elif t not in TYPES:
            raise TypeError("%s is not an acceptable type" % t)
        self.type = t

    def set_value(self, value, check=True):
        """
        Set the value.
        :param value: Value to set.
        :param check: Set to false to skip type checking.
        :return: True if successful.
        """
        set_val = True
        if self.type == "binary" and isinstance(value, string_types) and value.startswith(b"\x1Bbytes:"):
            value = bytearray(base64_decode(str(value[7:])))
        if check:
            set_val = self.check_type(value)
        if set_val:
            self.value = value
            self.updated_at = datetime.now()
            return True
        return False

    def has_value(self):
        return self.value is not None and self.type is not None

    def check_type(self, value):
        """
        Check the type of a variable compared to the type of this Value.
        :param value: Variable to check.
        :return: True if matches.
        """
        if self.type == "string":
            return isinstance(value, string_types)
        elif self.type == "number":
            return isinstance(value, Number)
        elif self.type == "int":
            return isinstance(value, Number)
        elif self.type == "uint":
            return isinstance(value, Number)
        elif self.type == "bool":
            # TODO(logangorence): Implement enum-like bool. Examples: "bool[disabled,enabled]" or "bool[on,off]"
            return type(value) == bool
        elif self.is_enum(self.type):
            return value in self.get_enum_values(self.type)
        elif self.type == "binary":
            return type(value) == bytearray or type(value) == str or type(value) == bytes
        elif self.type == "map":
            return type(value) == map
        elif self.type == "array":
            return type(value) == list
        elif self.type == "dynamic":
            return True
        else:
            raise ValueError("Type not supported")

    @staticmethod
    def build_enum(values):
        """
        Utility to convert list to String
        :param values: Values for conversion
        :return: Converted string. Example: enum[foo,bar]
        """
        if type(values) == list:
            return "enum[" + ",".join(values) + "]"
        # TODO(logangorence) Add support for Python Enum class.
        else:
            raise KeyError("build_enum called with non-list parameter.")

    @staticmethod
    def get_enum_values(enum):
        if enum.startswith("enum[") and enum.endswith("]"):
            return enum[5:-1].split(",")
        else:
            raise ValueError("Not an enum!")

    @staticmethod
    def is_enum(enum_type):
        if enum_type.startswith("enum[") and enum_type.endswith("]"):
            i = enum_type[5:-1]
            # noinspection PyBroadException
            try:
                i.split(",")
                return True
            except:
                return False
        return False


class ValueType:
    number = "number"
    int = "int"
    uint = "uint"
    string = "string"
    bool = "bool"
    enum = "enum"
    binary = "binary"
    map = "map"
    array = "array"
    dynamic = "dynamic"
