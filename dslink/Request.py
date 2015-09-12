from dslink.Node import Node
from dslink.Response import Response


class Request:
    def __init__(self, request):
        self.request = request
        self.rid = request["rid"]
        self.method = request["method"]

    def process(self):
        if self.method == "list":
            print("list")
            return Response({
                "rid": self.rid,
                "stream": "open",
                "updates": self.test().stream()
            })
        elif self.method == "subscribe":
            # TODO(logangorence)
            print("sub")
        elif self.method == "unsubscribe":
            # TODO(logangorence)
            print("unsub")
        elif self.method == "invoke":
            # TODO(logangorence)
            print("invoke")
        elif self.method == "set":
            # TODO(logangorence)
            print("set")


    @staticmethod
    def test():
        superRoot = Node(None, None)
        superRoot.add_child(Node("Create", superRoot))
        return superRoot
