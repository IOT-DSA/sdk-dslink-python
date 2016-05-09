from dslink.Response import Response
from dslink.Value import Value

from collections import OrderedDict
import logging
from threading import Lock


class Node:
    """
    Represents a Node on the Node structure.
    """

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
        self.transient = False
        self.value = Value()
        self.children = {}
        self.children_lock = Lock()
        self.config = OrderedDict([("$is", "node")])
        self.attributes = OrderedDict()
        self.streams = []
        self.removed_children = []
        self.removed_children_lock = Lock()
        # TODO(logangorence): Deprecate for v0.6
        self.set_value_callback = None
        # TODO(logangorence): Normalize path?
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

    def get_type(self):
        """
        Get the Node's value type.
        :return: Value type.
        """
        return self.get_config("$type")

    def set_type(self, t):
        """
        Set the Node's value type.
        :param t: Type to set.
        """
        self.value.set_type(t)
        self.set_config("$type", t)

    def get_value(self):
        """
        Get the Node's value.
        :return: Node value.
        """
        if self.value.type is "enum":
            return Value.build_enum(self.value.value)
        return self.value.value

    def set_value(self, value, trigger_callback=False, check=True):
        """
        Set the Node's value.
        :param value: Value to set.
        :param trigger_callback: Set to true if you want to trigger the value set callback.
        :param check: Turn type checking off if false.
        :return: True if the value was set.
        """
        # Set value and updated timestamp
        i = self.value.set_value(value, check)
        if i and (not self.standalone or self.link_is_active()):
            self.nodes_changed()
            self.update_subscribers_values()
            if trigger_callback:
                if hasattr(self.set_value_callback, "__call__"):
                    self.set_value_callback(node=self, value=value)
                try:
                    self.link.responder.profile_manager.get_profile(self.get_config("$is")).run_set_callback((self, value))
                except ValueError:
                    pass
        return i

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
        self.nodes_changed()
        self.config[key] = value
        self.update_subscribers()

    def get_attribute(self, key):
        """
        Get an attribute value.
        :param key: Key of attribute.
        :return: Value of attribute.
        """
        return self.attributes[key]

    def set_attribute(self, key, value):
        """
        Set an attribute value.
        :param key: Key of attribute.
        :param value: Value of attribute.
        """
        self.nodes_changed()
        self.attributes[key] = value
        self.update_subscribers()

    def set_transient(self, transient):
        """
        Set the node to be transient, which won't serialize it.
        :param transient: True if transient.
        """
        if type(transient) is not bool:
            raise TypeError("Transient must be bool")
        self.transient = transient

    def nodes_changed(self):
        """
        Set the Node structure as changed.
        """
        self.link.responder.nodes_changed = True

    def link_is_active(self):
        """
        Check if the link is active.
        :return: True if link is active.
        """
        return self.link.active

    def set_display_name(self, name):
        """
        Set the Node name.
        :param name: Node name.
        """
        if not isinstance(name, basestring):
            raise ValueError("Passed profile is not a string")
        self.set_config("$name", name)
        self.update_subscribers()

    def set_invokable(self, invokable):
        """
        Set invokable state.
        :param invokable: Invokable permit string or true for everyone can access.
        """
        if isinstance(invokable, basestring):
            self.set_config("$invokable", invokable)
        elif type(invokable) is bool and invokable:
            self.set_config("$invokable", "read")
        else:
            raise ValueError("Invokable is not a string or boolean")

    def set_parameters(self, parameters):
        """
        Set parameters for action.
        :param parameters: Parameters for action.
        """
        if type(parameters) is not list:
            raise ValueError("Parameters is not a list")
        self.set_config("$params", parameters)

    def set_columns(self, columns):
        """
        Set return columns for action.
        :param columns: Columns for action.
        """
        if type(columns) is not list:
            raise ValueError("Columns is not a list")
        self.set_config("$columns", columns)

    def set_profile(self, profile):
        """
        Set the Node's profile.
        :param profile: Node Profile.
        """
        if not isinstance(profile, basestring):
            raise ValueError("Passed profile is not a string")
        self.set_config("$is", profile)

    def set_writable(self, permission):
        """
        Set the writable permission.
        :param permission: Permission to set.
        """
        if isinstance(permission, basestring):
            self.set_config("$writable", permission)
        else:
            raise ValueError("Passed permission is not string")

    def stream(self):
        """
        Stream the Node.
        :return: Node stream.
        """
        out = []
        for key in self.config:
            value = self.config[key]
            if key == "$$password":
                value = None
            out.append([key, value])
        for key in self.attributes:
            value = self.attributes[key]
            out.append([key, value])
        with self.children_lock:
            for child in self.children:
                child = self.children[child]
                if child.value.has_value():
                    val = {
                        "value": child.value.value,
                        "ts": child.value.updated_at.isoformat()
                    }
                else:
                    val = {}
                child_data = dict(child.config)
                child_data.update(child.attributes)
                child_data.update(val)
                if "$$password" in child_data:
                    child_data["$$password"] = None
                out.append([
                    child.name,
                    child_data
                ])
        with self.removed_children_lock:
            for child in self.removed_children:
                out.append({
                    "name": child.name,
                    "change": "remove"
                })
                self.nodes_changed()
            del self.removed_children[:]
        return out

    def add_child(self, child):
        """
        Add a child to this Node.
        :param child: Child to add.
        """
        with self.children_lock:
            if child.name in self.children:
                raise ValueError("Child %s already exists in %s" % (child.name, self.path))
            self.children[child.name] = child
        self.nodes_changed()

        if self.standalone or self.link_is_active():
            self.update_subscribers()

    def remove_child(self, name):
        """
        Remove a child from this Node.
        :param name: Child Node name.
        """
        if name not in self.children:
            return
        with self.children_lock:
            self.removed_children.append(self.children.pop(name))
        self.update_subscribers()

    def has_child(self, name):
        """
        Check if this Node has child of name.
        :param name: Name of child.
        :return: True if the child of name exists.
        """
        return name in self.children

    def create_child(self, name):
        """
        Create a child node that inherits the root
        link and parent is this Node.
        :param name: Name of child node to create.
        :return: Child node.
        """
        child = Node(name, self)
        self.add_child(child)
        return child

    def get(self, path):
        """
        Get a Node from this position on the Node structure.
        :param path: Path of Node wanted.
        :return: Node of path.
        """
        if path == "/":
            return self
        elif path.startswith("/$"):
            return self
        elif path.startswith("/@"):
            return self
        else:
            try:
                try:
                    i = path.index("/", 2)
                    child = path[1:i]
                    return self.children[child].get(path[i:])
                except ValueError:
                    child = path[1:]
                    try:
                        return self.children[child]
                    except KeyError:
                        return None
            except KeyError:
                import traceback
                self.logger.warn("Non-existent Node requested %s on %s" % (path, self.path))

    def set_config_attr(self, path, value):
        """
        Set value/config/attribute on Node.
        :param path: Path of value to set.
        :param value: Value to set.
        """
        if path == "/" or path == self.path:
            self.set_value(value, trigger_callback=True)
        elif path.startswith("/$") or path.startswith(self.path + "/$"):
            self.set_config(path[2:], value)
        elif path.startswith("/@") or path.startswith(self.path + "/@"):
            self.set_attribute(path[2:], value)
        else:
            node = self.get(path)
            if node is not None:
                node.set_config_attr(path, value)

    def remove_config_attr(self, path):
        """
        Remove config/attribute on Node.
        :param path: Path of value to remove.
        """
        if path.startswith("/$") or path.startswith(self.path + "/$"):
            del self.config[path[2:]]
        elif path.startswith("/@") or path.startswith(self.path + "/@"):
            del self.config[path[2:]]
        else:
            self.get(path).remove_config_attr(path)

    def is_subscribed(self):
        """
        Check whether the Node is subscribed to.
        :return: True if the Node is subscribed to.
        """
        sub = self.link.responder.subscription_manager.get_sub(self.path)
        if sub is None:
            return False
        return len(sub.sid_qos) is not 0

    def invoke(self, params):
        """
        Invoke the Node.
        :param params: Parameters of invoke.
        :return: Columns and values
        """
        self.logger.debug("%s invoked, with parameters: %s" % (self.path, params))
        try:
            # noinspection PyCallingNonCallable
            return (self.config["$columns"] if "$columns" in self.config else []), self.link.responder.profile_manager.get_profile(self.get_config("$is")).run_callback((self, params))
        except ValueError:
            return [], []

    def update_subscribers(self):
        """
        Send subscription updates.
        """
        responses = []
        for stream in self.streams:
            responses.append(Response({
                "rid": stream,
                "stream": "open",
                "updates": self.stream()
            }).get_stream())
        if responses:
            self.link.wsp.sendMessage({
                "responses": responses
            })

    def update_subscribers_values(self):
        """
        Update all Subscribers of a Value change.
        """
        if self.value.has_value():
            self.link.responder.subscription_manager.send_value_update(self)

    def to_json(self):
        """
        Convert to an object that is saved to JSON.
        :return: JSON object.
        """
        out = {}

        for key in self.config:
            out[key] = self.config[key]
        for key in self.attributes:
            out[key] = self.attributes[key]
        if self.value.has_value():
            out["?value"] = self.value.value
        for child in self.children:
            if not self.children[child].transient:
                out[child] = self.children[child].to_json()

        return out

    @staticmethod
    def from_json(obj, root, name, link=None):
        """
        Convert a JSON object to a String
        :param obj: Node Object.
        :param root: Root Node.
        :param name: Node Name.
        :param link: Created Node's link.
        :return: Node that was created.
        """
        node = Node(name, root)
        if link is not None:
            node.link = link

        if type(obj) is dict:
            for prop in obj:
                if prop.startswith("$"):
                    if prop == "$type":
                        node.set_type(obj[prop])
                    else:
                        node.set_config(prop, obj[prop])
                elif prop.startswith("@"):
                    node.set_attribute(prop, obj[prop])
                elif prop == "?value":
                    node.set_value(obj[prop], check=False)
                else:
                    node.add_child(Node.from_json(obj[prop], node, prop))

        return node

    @staticmethod
    def normalize_path(path, leading):
        """
        :param path: Path to normalize.
        :param leading: True if leading forward slash is kept/added, false if not.
        :return: Normalized path.
        """
        if not leading and path.startswith("/"):
            path = path[1:]
        elif leading and not path.startswith("/"):
            path = "/" + path
        if path.endswith("/"):
            path = path[:-1]

        return path


class RemoteNode(Node):
    def __init__(self, name, parent, parent_path=None):
        Node.__init__(self, name, parent)
        if parent_path is not None:
            self.path = parent_path + name

    def set_value(self, value, trigger_callback=False, check=True):
        # TODO(logangorence): Set value.
        pass

    def update_subscribers(self):
        pass

    def update_subscribers_values(self):
        pass

    def add_child(self, child):
        pass

    def nodes_changed(self):
        pass

    def link_is_active(self):
        return False

    def from_serialized(self, serialized):
        for a in serialized:
            if type(a) is not list:
                continue
            k = a[0]
            v = a[1]
            if k.startswith("$"):
                self.set_config(k, v)
            elif k.startswith("@"):
                self.set_attribute(k, v)
            else:
                child = RemoteNode(k, self)
                for i in v:
                    if i.startswith("$"):
                        child.set_config(i, v[i])
                    elif i.startswith("@"):
                        child.set_attribute(i, v[i])
                Node.add_child(self, child)
