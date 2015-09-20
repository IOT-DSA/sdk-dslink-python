import logging

import dslink
from dslink.Response import Response


class Request:
    def __init__(self, request):
        self.logger = logging.getLogger("DSLink")
        self.request = request
        self.rid = request["rid"]
        self.method = request["method"]

    def process(self):
        if self.method == "list":
            self.logger.debug("List method")
            return Response({
                "rid": self.rid,
                "stream": "open",
                "updates": dslink.DSLink.DSLink.super_root.get(self.request["path"]).stream()
            })
        elif self.method == "subscribe":
            # TODO(logangorence) Implement subscriptions
            self.logger.debug("Subscribe method")
            return Response({
                "rid": self.rid,
                "stream": "closed"
            })
        elif self.method == "unsubscribe":
            # TODO(logangorence) Implement unsubscriptions
            self.logger.debug("Unsubscribe method")
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
            # TODO(logangorence) Implement proper closing
            self.logger.debug("Close method")
            return Response({
                "rid": self.rid,
                "stream": "closed"
            })
