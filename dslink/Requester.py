from dslink.Response import *


class Requester:
    def __init__(self, link):
        self.link = link
        self.request_manager = RequestManager()
        self.rid = 1
        self.sub_paths = {}

    def get_next_rid(self):
        """
        Get the next rid in the sequence. Initially starts from 1.
        :return: Next rid in sequence.
        """
        r = self.rid
        self.rid += 1
        return r

    def list(self, path, callback):
        """
        List a remote node.
        :param path: Request path.
        :param callback: Response callback.
        """
        rid = self.get_next_rid()
        self.link.wsp.sendMessage({
            "requests": [
                {
                    "rid": rid,
                    "method": "list",
                    "path": path
                }
            ]
        }, self)
        self.request_manager.start_request(rid, "list", callback, metadata={
            "path": path
        })

    def set(self, path, value, permit=None, callback=None):
        """
        Set a remote value.
        :param path: Path of value.
        :param value: Value to set.
        :param permit: Maximum permission of set.
        :param callback: Response callback.
        """
        rid = self.get_next_rid()
        i = {
            "rid": rid,
            "method": "set",
            "path": path,
            "value": value
        }
        if permit is not None:
            i["permit"] = permit
        self.link.wsp.sendMessage({
            "requests": [
                i
            ]
        })
        if callback:
            self.request_manager.start_request(rid, "set", callback)

    def remove(self, path, callback=None):
        """
        Remove a remote value.
        :param path: Path of value.
        :param callback: Response callback.
        """
        rid = self.get_next_rid()
        self.link.wsp.sendMessage({
            "rid": rid,
            "method": "remove",
            "path": path
        })
        if callback:
            self.request_manager.start_request(rid, "remove", callback)

    def invoke(self, path, permit=None, params=None, callback=None):
        """
        Invoke a remote method.
        :param path: Path of node.
        :param permit: Maximum permission of invoke.
        :param params: Parameters of invoke.
        :param callback: Response callback.
        """
        rid = self.get_next_rid()
        i = {
            "rid": rid,
            "method": "invoke",
            "path": path
        }
        if permit is not None:
            i["permit"] = permit
        if params is not None:
            i["params"] = params
        self.link.wsp.sendMessage({
            "requests": [
                i
            ]
        })
        if callback:
            self.request_manager.start_request(rid, "invoke", callback)

    def subscribe(self, path, callback):
        """
        Subscribe to a remote Node.
        :param path: Path of Node.
        :param callback: Response callback.
        """
        pass

    def unsubscribe(self, path):
        """
        Unsubscribe to a remote Node.
        :param path: Path of Node.
        """
        if path in self.sub_paths:
            sid = self.sub_paths[path]
            rid = self.get_next_rid()
            self.link.wsp.sendMessage({
                "requests": [
                    {
                        "rid": rid,
                        "method": "unsubscribe",
                        "sids": [
                            sid
                        ]
                    }
                ]
            })
        else:
            raise ValueError("Path is not subscribed.")

    def close(self, rid):
        """
        Close a stream.
        :param rid: ID of request.
        """
        self.link.wsp.sendMessage({
            "requests": [
                {
                    "rid": rid,
                    "method": "close"
                }
            ]
        })


class RequestManager:
    """
    Manages outgoing requests and callbacks.
    """

    def __init__(self):
        """
        Constructor of RequestManager.
        """
        self.requests = {}

    def start_request(self, rid, type, callback, metadata=None):
        """
        Start a Request.
        :param rid: RID of Request.
        :param type: Type of Request.
        :param callback: Callback to invoke.
        :param metadata: Metadata for request.
        """
        if not metadata:
            metadata = {}
        self.requests[rid] = {
            "type": type,
            "callback": callback,
            "metadata": metadata
        }

    def stop_request(self, rid):
        """
        Stop a Request.
        :param rid: RID of Request.
        """
        del self.requests[rid]

    def invoke_request(self, rid, data):
        """
        Invoke a Request.
        :param rid: RID of Request.
        :param data: Data of Request.
        """
        request = self.requests[rid]
        response = data
        if request["type"] == "list":
            response = ListResponse(data, request["metadata"]["path"])
        request["callback"](response)
