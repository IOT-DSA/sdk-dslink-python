import logging

from dslink.Response import Response


class Request:
    """
    Class that handles incoming requests.
    """

    def __init__(self, request, link):
        self.logger = logging.getLogger("DSLink")
        self.request = request
        self.link = link
        self.rid = request["rid"]
        self.method = request["method"]

    def process(self):
        """
        Process the request.
        :return: Response adequate the the request.
        """
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
                node = self.link.super_root.get(sub["path"])
                if node is not None:
                    self.link.subman.subscribe(node, sub["sid"])
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
            self.logger.debug("Invoke method")
            columns, values = self.link.super_root.get(self.request["path"]).invoke(self.request["params"])
            # TODO(logangorence) Implement streaming invokes
            return Response({
                "rid": self.rid,
                "columns": columns,
                "updates": values,
                "stream": "closed"
            })
        elif self.method == "set":
            self.logger.debug("Set method")
            # TODO(logangorence) Handle permit
            # TODO(logangorence) Handle improper value type
            self.link.super_root.set_config_attr(self.request["path"], self.request["value"])
            return Response({
                "rid": self.rid,
                "stream": "closed"
            })
        elif self.method == "remove":
            self.logger.debug("Remove method")
            self.link.super_root.remove_config_attr(self.request["path"])
            return Response({
                "rid": self.rid,
                "stream": "closed"
            })
        elif self.method == "close":
            self.logger.debug("Close method")
            self.link.strman.close_stream(self.rid)
            return Response({
                "rid": self.rid,
                "stream": "closed"
            })
        else:
            raise NotImplementedError("Method %s is not implemented" % self.method)
