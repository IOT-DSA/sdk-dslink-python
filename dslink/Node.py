from collections import OrderedDict
import logging

from dslink.Response import Response
from dslink.Value import Value


class Node:
    """ Represents a Node on the Node structure. """

    def __init__(self, name, parent, standalone=False):
        """
        Node Constructor.
        :param name: Node name.
        :param parent: Node parent.
        :param standalone: Standalone Node structure.
        """
        self.logger = logging.getLogger("DSLink")
        if parent is not None:
            self.link = parent.link
        self.parent = parent
        self.standalone = standalone
        self.value = Value()
        self.children = {}
        self.config = OrderedDict([("$is", "node")])
        self.attributes = OrderedDict()
        self.subscribers = []
        self.streams = []
        self.invoke_callback = None
        if parent is not None:
            self.name = name
            if parent.path.endswith("/"):
                self.path = parent.path + name
            else:
                self.path = parent.path + "/" + name
        else:
            if name is not None:
                self.name = name
                self.path = "/" + name
            else:
                self.name = ""
                self.path = ""

    def has_value(self):
        """
        Check if the Node has a value.
        :return: True if the Node has a value.
        """
        return self.value.type is not None

    def get_type(self):
        """
        Get the Node's value type.
        :return: Value type.
        """
        return self.config["$type"]

    def set_type(self, t):
        """
        Set the Node's value type.
        :param t: Type to set.
        """
        # TODO(logangorence) Check for valid type
        self.value.set_type(t)
        self.config["$type"] = t

    def get_value(self):
        """
        Get the Node's value.
        :return: Node value.
        """
        if self.value.type is "enum":
            return Value.build_enum(self.value.value)
        return self.value.value

    def set_value(self, value):
        """
        Set the Node's value.
        :param value: Value to set.
        """
        # Set value and updated timestamp
        if self.value.set_value(value) and (not self.standalone or self.link.active):
            # TODO(logangorence) Clean this up
            # Update any subscribers
            for s in self.subscribers:
                self.link.wsp.sendMessage({
                    "responses": [
                        {
                            "rid": 0,
                            "updates": [
                                [
                                    s,
                                    value,
                                    self.value.updated_at.isoformat()
                                ]
                            ]
                        }
                    ]
                })

    def get_config(self, key):
        """
        Get a config value.
        :param key: Key of config.
        :return: Value of config.
        """
        return self.config[key]

    def set_config(self, key, value):
        """
        Set a config value.
        :param key: Key of config.
        :param value: Value of config.
        """
        self.config[key] = value
        self.update_subscribers()

    def set_invokable(self, invokable):
        """
        Set invokable state.
        :param invokable: Invokable permit.
        :return: True on success.
        """
        if type(invokable) is str:
            self.set_config("$invokable", invokable)
            return True
        return False

    def set_parameters(self, parameters):
        """
        Set parameters for action.
        :param params: Parameters for action.
        :return: True on success.
        """
        if type(parameters) is list:
            self.set_config("$params", parameters)
            return True
        return False

    def set_columns(self, columns):
        """
        Set return columns for action.
        :param columns: Columns for action.
        :return: True on success.
        """
        if type(columns) is list:
            self.set_config("$columns", columns)
            return True
        return False

    def stream(self):
        """
        Stream the Node.
        :return: Node stream.
        """
        out = []
        for k in self.config:
            out.append([k, self.config[k]])
        for child in self.children:
            child = self.children[child]
            if child.has_value():
                val = {
                    "value": child.value.value,
                    "ts": child.value.updated_at.isoformat()
                }
            else:
                val = {}
            l = len(child.path.split("/")) - 1
            i = dict(child.config)
            i.update(child.attributes)
            i.update(val)
            out.append([
                child.path.split("/")[l],
                i
            ])
        return out

    def add_child(self, child):
        """
        Add a child to this Node.
        :param child: Child to add.
        """
        self.children[child.name] = child

        if self.standalone or self.link.active:
            self.update_subscribers()

    def get(self, path):
        """
        Get a Node from this position on the Node structure.
        :param path: Path of Node wanted.
        :return: Node of path.
        """
        if path == "/":
            return self
        else:
            try:
                try:
                    i = path.index("/", 2)
                    child = path[1:i]
                    return self.children[child].get(path[i:])
                except ValueError:
                    child = path[1:]
                    return self.children[child]
            except KeyError:
                self.logger.warn("Non-existent Node requested %s" % path)

    def is_subscribed(self):
        """
        Is the Node subscribed to?
        :return: True if the Node is subscribed to.
        """
        return len(self.subscribers) is not 0

    def invoke(self, params):
        """
        Invoke the Node.
        :param params: Parameters of invoke.
        :return: Columns and values
        """
        self.logger.debug("%s invoked, with parameters: %s" % (self.path, params))
        # noinspection PyCallingNonCallable
        return (self.config["$columns"] if "$columns" in self.config else []), self.invoke_callback(params)

    def set_invoke_callback(self, callback):
        """
        Set the invoke callback.
        :param callback: Callback to call on an invoke method.
        """
        if hasattr(callback, "__call__"):
            self.invoke_callback = callback
        else:
            raise ValueError("Provided callback is not a function.")

    def update_subscribers(self):
        """
        Send subscription updates.
        """
        for stream in self.streams:
            self.link.wsp.sendMessage({
                "responses": [
                    Response({
                        "rid": stream,
                        "stream": "open",
                        "updates": self.stream()
                    }).get_stream()
                ]
            })
