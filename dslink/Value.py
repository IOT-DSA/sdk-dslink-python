from datetime import datetime


class Value:
    def __init__(self):
        self.value = None
        self.type = None
        self.updated_at = None

    def set_type(self, t):
        # TODO(logangorence) Check for valid type
        self.type = t

    def set_value(self, value):
        if self.check_type(value):
            self.value = value
            self.updated_at = datetime.now()
            return True
        return False

    def check_type(self, value):
        # TODO(logangorence): Finish implementing types
        if self.type == "string":
            return type(value) == str
        elif self.type == "number":
            return type(value) == int or type(value) == float
        elif self.type == "int":
            return type(value) == int
        elif self.type == "bool":
            return type(value) == bool
