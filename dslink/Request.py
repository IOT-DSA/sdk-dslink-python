import logging

from dslink.Response import Response


class Request:
    def __init__(self, request, link):
        self.logger = logging.getLogger("DSLink")
        self.request = request
        self.link = link
        self.rid = request["rid"]
        self.method = request["method"]

    def process(self):
        if self.method == "list":
            self.logger.debug("List method")
            node = self.link.super_root.get(self.request["path"])
            if node is not None:
                self.link.strman.open_stream(node, self.rid)
                return Response({
                    "rid": self.rid,
                    "stream": "open",
                    "updates": node.stream()
                })
            else:
                return Response({
                    "rid": self.rid,
                    "stream": "closed"
                })
        elif self.method == "subscribe":
            self.logger.debug("Subscribe method")
            for sub in self.request["paths"]:
                self.link.subman.subscribe(self.link.super_root.get(sub["path"]), sub["sid"])
                self.logger.debug("Subscription added")
            return Response({
                "rid": self.rid,
                "stream": "closed"
            })
        elif self.method == "unsubscribe":
            self.logger.debug("Unsubscribe method")
            for sid in self.request["sids"]:
                self.link.subman.unsubscribe(sid)
            return Response({
                "rid": self.rid,
                "stream": "closed"
            })
        elif self.method == "invoke":
            # TODO(logangorence) Implement invoking
            self.logger.debug("Invoke method")
        elif self.method == "set":
            # TODO(logangorence) Implement setting
            self.logger.debug("Set method")
        elif self.method == "close":
            self.logger.debug("Close method")
            self.link.strman.close_stream(self.rid)
            return Response({
                "rid": self.rid,
                "stream": "closed"
            })
