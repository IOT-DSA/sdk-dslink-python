import dslink
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
                "updates": dslink.DSLink.DSLink.super_root.get(self.request["path"]).stream()
            })
        elif self.method == "subscribe":
            # TODO(logangorence)
            print("sub")
        elif self.method == "unsubscribe":
            # TODO(logangorence)
            print("unsubscribe")
        elif self.method == "invoke":
            # TODO(logangorence)
            print("invoke")
        elif self.method == "set":
            # TODO(logangorence)
            print("set")
        elif self.method == "close":
            # TODO(logangorence)
            print("close")
            return Response({
                "rid": self.rid,
                "stream": "closed"
            })
