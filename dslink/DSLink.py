import argparse
import base64
import logging

from dslink.Crypto import Keypair
from dslink.Handshake import Handshake
from dslink.Node import Node
from dslink.WebSocket import WebSocket


class DSLink:
    """
    Base DSLink class which creates the node structure,
    subscription/stream manager, and connects to the broker.
    """

    def __init__(self, config):
        """
        Construct for DSLink.
        :param config: Configuration object.
        """
        # DSLink Configuration
        self.config = config

        # Node tree
        self.super_root = Node("", None)
        self.super_root.link = self

        # Logger setup
        self.logger = self.create_logger("DSLink", self.config.log_level)
        self.logger.info("Starting DSLink")

        # Managers setup
        self.subman = SubscriptionManager()
        self.strman = StreamManager()
        self.reqman = RequestManager()

        # DSLink setup
        self.rid = 1
        self.keypair = Keypair()
        self.handshake = Handshake(self, config.name, config.broker, self.keypair, config.responder, config.requester)
        self.server_config = self.handshake.run_handshake()
        self.salt = self.server_config["salt"]
        self.dsid = self.handshake.get_dsid()
        self.shared_secret = self.keypair.keypair.get_ecdh_key(
            base64.urlsafe_b64decode(self.add_padding(self.server_config["tempKey"]).encode("utf-8")))

        # Connection setup
        self.active = False
        self.wsp = None
        self.websocket = WebSocket(self)

        self.logger.info("Started DSLink")

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
        """
        if not self.config.requester:
            raise ValueError("Requester is not enabled.")
        rid = self.get_next_rid()
        self.wsp.sendMessage({
            "requests": [
                {
                    "rid": rid,
                    "method": "list",
                    "path": path
                }
            ]
        }, self)
        self.reqman.start_request(rid, callback)

    def set(self, path, value, permit=None, callback=None):
        """
        Set a remote value.
        :param path: Path of value.
        :param value: Value to set.
        :param permit: Maximum permission of set.
        :param callback: Response callback.
        """
        if not self.config.requester:
            raise ValueError("Requester is not enabled.")
        rid = self.get_next_rid()
        i = {
            "rid": rid,
            "method": "set",
            "path": path,
            "value": value
        }
        if permit is not None:
            i["permit"] = permit
        self.wsp.sendMessage({
            "requests": [
                i
            ]
        })
        if callback:
            self.reqman.start_request(rid, callback)

    def remove(self, path, callback=None):
        """
        Remove a remote value.
        :param path: Path of value.
        :param callback: Response callback.
        """
        if not self.config.requester:
            raise ValueError("Requester is not enabled.")
        rid = self.get_next_rid()
        self.wsp.sendMessage({
            "rid": rid,
            "method": "remove",
            "path": path
        })
        if callback:
            self.reqman.start_request(rid, callback)

    def invoke(self, path, permit=None, params=None, callback=None):
        """
        Invoke a remote method.
        :param path: Path of node.
        :param permit: Maximum permission of invoke.
        :param params: Parameters of invoke.
        :param callback: Response callback.
        """
        if not self.config.requester:
            raise ValueError("Requester is not enabled.")
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
        self.wsp.sendMessage({
            "requests": [
                i
            ]
        })
        if callback:
            self.reqman.start_request(rid, callback)

    # TODO(logangorence): Subscribe method.

    # TODO(logangorence): Unsubscribe method.

    def close(self, rid):
        """
        Close a stream.
        :param rid: ID of request.
        """
        if not self.config.requester:
            raise ValueError("Requester is not enabled.")
        self.wsp.sendMessage({
            "requests": [
                {
                    "rid": rid,
                    "method": "close"
                }
            ]
        })

    @staticmethod
    def create_logger(name, log_level=logging.INFO):
        """
        Create a logger with the specified name.
        :param name: Logger name.
        :param log_level: Output Logger level.
        :return: Logger instance.
        """
        # Logger setup
        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        ch.setLevel(log_level)
        logger = logging.getLogger(name)
        logger.setLevel(log_level)
        logger.addHandler(ch)
        return logger

    @staticmethod
    def add_padding(string):
        """
        Add padding to a URL safe base64 string.
        :param string:
        :return:
        """
        while len(string) % 4 != 0:
            string += "="
        return string


class SubscriptionManager:
    """
    Manages subscriptions to Nodes.
    """

    def __init__(self):
        """
        Constructor of SubscriptionManager.
        """
        self.subscriptions = {}

    def subscribe(self, node, sid):
        """
        Store a Subscription to a Node.
        :param node: Node to subscribe to.
        :param sid: SID of Subscription.
        """
        self.subscriptions[sid] = node
        self.subscriptions[sid].add_subscriber(sid)

    def unsubscribe(self, sid):
        """
        Remove a Subscription to a Node.
        :param sid: SID of Subscription.
        """
        try:
            self.subscriptions[sid].remove_subscriber(sid)
            del self.subscriptions[sid]
        except KeyError:
            logging.getLogger("DSlink").debug("Unknown sid %s" % sid)


class StreamManager:
    """
    Manages streams for Nodes.
    """

    def __init__(self):
        """
        Constructor of StreamManager.
        """
        self.streams = {}

    def open_stream(self, node, rid):
        """
        Open a Stream.
        :param node: Node to handle streaming.
        :param rid: RID of Stream.
        """
        self.streams[rid] = node
        self.streams[rid].streams.append(rid)

    def close_stream(self, rid):
        """
        Close a Stream.
        :param rid: RID of Stream.
        """
        try:
            self.streams[rid].streams.remove(rid)
            del self.streams[rid]
        except KeyError:
            logging.getLogger("DSLink").debug("Unknown rid %s" % rid)


class RequestManager:
    """
    Manages outgoing requests and callbacks.
    """

    def __init__(self):
        """
        Constructor of RequestManager.
        """
        self.requests = {}

    def start_request(self, rid, callback):
        """
        Start a Request.
        :param rid: RID of Request.
        :param callback: Callback to invoke.
        """
        self.requests[rid] = callback

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
        self.requests[rid](data)


class Configuration:
    """
    Provides configuration to the DSLink.
    """

    def __init__(self, name, responder=False, requester=False, ping_time=30):
        """
        Object that contains configuration for the DSLink.
        :param name: DSLink name.
        :param responder: True if acts as responder, default is False.
        :param requester: True if acts as requester, default is False.
        :param ping_time: Time between pings, default is 30.
        """
        if not responder and not requester:
            print "DSLink is neither responder nor requester. Exiting now."
            exit(1)
        parser = argparse.ArgumentParser()
        parser.add_argument("--broker", default="http://localhost:8080/conn")
        parser.add_argument("--log", default="info")
        args = parser.parse_args()
        self.name = name
        self.broker = args.broker
        self.log_level = args.log.lower()
        self.responder = responder
        self.requester = requester
        self.ping_time = ping_time

        if self.log_level == "critical":
            self.log_level = logging.CRITICAL
        elif self.log_level == "error":
            self.log_level = logging.ERROR
        elif self.log_level == "warning":
            self.log_level = logging.WARNING
        elif self.log_level == "info":
            self.log_level = logging.INFO
        elif self.log_level == "debug":
            self.log_level = logging.DEBUG
        elif self.log_level == "none":
            self.log_level = logging.NOTSET
