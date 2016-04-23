from dslink.Response import *


class Requester:
    def __init__(self, link):
        self.link = link
        self.request_manager = RequestManager()
        self.subscription_manager = RemoteSubscriptionManager()
        self.rid = 1
        self.sid = 0

    def get_next_rid(self):
        """
        Get the next rid in the sequence. Initially starts from 1.
        :return: Next rid in sequence.
        """
        r = self.rid
        self.rid += 1
        return r

    def get_next_sid(self):
        """
        Get the next sid in the sequence. Initially starts from 0.
        :return: Next sid in the sequence.
        """
        s = self.sid
        self.sid += 1
        return s

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

    def subscribe(self, path, callback, qos=0):
        """
        Subscribe to a remote Node.
        :param path: Path of Node.
        :param callback: Response callback.
        :param qos: Quality of Service.
        """
        if type(path) is not str:
            raise ValueError("Unsupported path type.")
        rid = self.get_next_rid()
        sid = self.get_next_sid()
        self.subscription_manager.subscribe(sid, path, callback, qos)
        self.link.wsp.sendMessage({
            "requests": [
                {
                    "rid": rid,
                    "method": "subscribe",
                    "paths": [
                        {
                            "path": path,
                            "sid": sid,
                            "qos": qos
                        }
                    ]
                }
            ]
        })

    def unsubscribe(self, path):
        """
        Unsubscribe to a remote Node.
        :param path: Path of Node.
        """
        if type(path) is str:
            sid = self.subscription_manager.get_sid_by_path(path)
            self.subscription_manager.unsubscribe(sid)
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
            raise ValueError("Unsupported path type.")

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


class RemoteSubscriptionManager:
    def __init__(self):
        self.subscriptions = {}

    def subscribe(self, sid, path, callback, qos=0):
        """
        Subscribe to a Node.
        :param sid: Subscription ID.
        :param path: Path of Node.
        :param callback: Callback to run with value.
        :param qos: Quality of Service.
        """
        if not hasattr(callback, "__call__"):
            raise ValueError("Passed callback is not callable.")
        elif sid in self.subscriptions:
            raise ValueError("Sid %s is already in use." % sid)
        self.subscriptions[sid] = {
            "path": path,
            "callback": callback,
            "qos": qos
        }

    def unsubscribe(self, sid):
        """
        Unsubscribe from a Node.
        :param sid: Subscription ID.
        """
        if sid not in self.subscriptions:
            raise ValueError("Sid %s not in use." % sid)
        del self.subscriptions[sid]

    def get_sid_by_path(self, path):
        """
        Get a Subscription ID by path.
        :param path: Path of Node.
        :return: Subscription ID.
        """
        for sid in self.subscriptions:
            meta = self.subscriptions[sid]
            if meta["path"] == path:
                return sid

    def run_callback(self, sid, value, time, count=0, sum=0, min=0, max=0):
        """
        Run a subscription's callback.
        :param sid: Subscription ID.
        :param value: Value.
        :param time: Updated at time.
        :param count: Number of values merged.
        :param sum: Sum of values merged.
        :param min: Minimum value of values merged.
        :param max: Maximum value of values merged.
        """
        self.subscriptions[sid]["callback"]((value, time, count, sum, min, max))
