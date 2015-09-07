class Node:
    def __init__(self, name, parent):
        self.parent = parent
        self.children = {}
        self.config = {
            "$is": "node"
        }
        self.attributes = {}
        if parent is not None:
            self.name = name
            self.path = parent.path + "/" + name
        else:
            if name is not None:
                self.name = name
                self.path = "/" + name
            else:
                self.name = ""
                self.path = ""

    def has_value(self):
        return False

    def stream(self):
        out = dict(self.config)
        out.update(self.attributes)
        out = self.o_to_a(out)
        for child in self.children:
            child = self.children[child]
            if (child.has_value()):
                val = {
                    "value": child.value,
                    # TODO(logangorence) last updated timestamp
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

    @staticmethod
    def o_to_a(obj):
        arr = []
        for key in obj:
            arr.append(key)
            arr.append(obj[key])
        return arr
