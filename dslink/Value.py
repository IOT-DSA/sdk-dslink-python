from datetime import datetime
import logging

TYPES = [
    "number",
    "int",
    "uint",
    "string",
    "bool",
    "enum",
    "bytes",
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
        if t not in TYPES:
            raise TypeError("%s is not an acceptable type" % t)
        self.type = t

    def set_value(self, value):
        """
        Set the value.
        :param value: Value to set.
        :return: True if successful.
        """
        if self.check_type(value):
            self.value = value
            self.updated_at = datetime.now()
            return True
        return False

    def check_type(self, value):
        """
        Check the type of a variable compared to the type of this Value.
        :param value: Variable to check.
        :return: True if matches.
        """
        # TODO(logangorence): Finish implementing types
        if self.type == "string":
            return type(value) == str
        elif self.type == "number":
            return type(value) == int or type(value) == float
        elif self.type == "int":
            return type(value) == int
        elif self.type == "bool":
            # TODO(logangorence): Implement enum-like bool.
            return type(value) == bool
        elif self.type == "enum":
            return type(value) == list
        elif self.type == "dynamic":
            # TODO(logangorence): Check to ensure that the type is still a valid one that we accept.
            return True

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
