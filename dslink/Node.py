from dslink.Value import Value


class Node:
    def __init__(self, name, parent):
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
        return self.value.type is not None

    def set_type(self, t):
        # TODO(logangorence) Check for valid type
        self.value.set_type(t)
        self.config["$type"] = t

    def set_value(self, value):
        # Set value and updated timestamp
        if self.value.set_value(value):
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

    def stream(self):
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
        self.children[child.name] = child

    def get(self, path):
        if path == "/":
            return self
        else:
            try:
                i = path.index("/", 2)
                child = path[1:i]
                return self.children[child].get(path[i:])
            except ValueError:
                child = path[1:]
                return self.children[child]

    @staticmethod
    def o_to_a(obj):
        arr = []
        for key in obj:
            arr.append(key)
            arr.append(obj[key])
        return arr
