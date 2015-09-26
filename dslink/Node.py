import logging

from dslink.Response import Response
from dslink.Value import Value


class Node:
    """ Represents a Node on the Node structure. """
    def __init__(self, name, parent):
        """
        Node Constructor.
        :param name: Node name.
        :param parent: Node parent.
        """
        self.logger = logging.getLogger("DSLink")
        if parent is not None:
            self.link = parent.link
        self.parent = parent
        self.value = Value()
        self.children = {}
        self.config = {
            "$is": "node"
        }
        self.attributes = {}
        self.subscribers = []
        self.streams = []
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

    def set_type(self, t):
        """
        Set the Node's value type.
        :param t: Type to set.
        """
        # TODO(logangorence) Check for valid type
        self.value.set_type(t)
        self.config["$type"] = t

    def set_value(self, value):
        """
        Set the Node's value.
        :param value: Value to set.
        """
        # Set value and updated timestamp
        if self.value.set_value(value) and self.link.active:
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

    def set_config(self, key, value):
        self.config[key] = value

    def set_invokable(self, invokable):
        self.set_config("$invokable", invokable)

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

        if self.link.active:
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
