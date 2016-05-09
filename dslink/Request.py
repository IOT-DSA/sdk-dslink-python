import datetime

from dslink.Response import Response

import logging


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
            node = self.link.responder.get_super_root().get(self.request["path"])
            resp = Response({
                "rid": self.rid,
                "stream": "open"
            })
            if node is not None:
                self.link.responder.stream_manager.open_stream(node, self.rid)
                resp.json["updates"] = node.stream()
            else:
                resp.json["updates"] = [
                    [
                        "$disconnectedTs",
                        datetime.datetime.now().isoformat()
                    ]
                ]
            return resp
        elif self.method == "subscribe":
            self.logger.debug("Subscribe method")
            for sub in self.request["paths"]:
                node = self.link.responder.get_super_root().get(sub["path"])
                if node is not None:
                    qos = 0
                    if "qos" in sub:
                        qos = sub["qos"]
                    self.link.responder.subscription_manager.add_value_sub(node, sub["sid"], qos)
                    self.logger.debug("Subscription added")
            return Response({
                "rid": self.rid,
                "stream": "closed"
            })
        elif self.method == "unsubscribe":
            for sid in self.request["sids"]:
                self.logger.debug("Unsubscribe from sid %s" % sid)
                self.link.responder.subscription_manager.remove_value_sub(sid)
            return Response({
                "rid": self.rid,
                "stream": "closed"
            })
        elif self.method == "invoke":
            self.logger.debug("Invoke method")
            # TODO(logangorence) Handle not implemented profiles
            node_invoke = self.link.responder.get_super_root().get(self.request["path"])
            if node_invoke is not None:
                columns, values = node_invoke.invoke(self.request["params"])
            else:
                self.logger.debug("Invoke on non-existant node %s." % self.request["path"])
                columns = []
                values = []
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
            self.link.responder.get_super_root().set_config_attr(self.request["path"], self.request["value"])
            return Response({
                "rid": self.rid,
                "stream": "closed"
            })
        elif self.method == "remove":
            self.logger.debug("Remove method")
            self.link.responder.get_super_root().remove_config_attr(self.request["path"])
            return Response({
                "rid": self.rid,
                "stream": "closed"
            })
        elif self.method == "close":
            self.logger.debug("Close method")
            self.link.responder.stream_manager.close_stream(self.rid)
            return Response({
                "rid": self.rid,
                "stream": "closed"
            })
        else:
            raise NotImplementedError("Method %s is not implemented" % self.method)
