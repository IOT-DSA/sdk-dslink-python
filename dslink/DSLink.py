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
        # Temporary Node tree
        self.super_root = Node("", None)
        self.super_root.link = self

        # Logger setup
        self.logger = self.create_logger("DSLink")
        self.logger.info("Starting DSLink")

        # Subscription/stream setup
        self.subman = SubscriptionManager()
        self.strman = StreamManager()

        # DSLink setup
        self.config = config
        self.keypair = Keypair()
        self.handshake = Handshake(self, config.name, config.broker, self.keypair, config.responder, config.requester)
        self.server_config = self.handshake.run_handshake()
        self.salt = self.server_config["salt"]
        self.dsid = self.handshake.get_dsid()
        self.shared_secret = self.keypair.keypair.get_ecdh_key(
            base64.urlsafe_b64decode(self.add_padding(self.server_config["tempKey"])))

        # Connection setup
        self.active = False
        self.websocket = WebSocket(self)

    @staticmethod
    def create_logger(name):
        # Logger setup
        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        ch.setLevel(logging.DEBUG)
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(ch)
        return logger

    @staticmethod
    def add_padding(string):
        while len(string) % 4 != 0:
            string += "="
        return string


class SubscriptionManager:
    """ Manages subscriptions to Nodes. """

    def __init__(self):
        self.subscriptions = {}

    def subscribe(self, node, sid):
        self.subscriptions[sid] = node
        self.subscriptions[sid].subscribers.append(sid)

    def unsubscribe(self, sid):
        self.subscriptions[sid].subscribers.remove(sid)
        self.subscriptions[sid] = None


class StreamManager:
    """ Manages streams for Nodes. """

    def __init__(self):
        self.streams = {}

    def open_stream(self, node, rid):
        self.streams[rid] = node
        self.streams[rid].streams.append(rid)

    def close_stream(self, rid):
        try:
            self.streams[rid].streams.remove(rid)
            self.streams[rid] = None
        except KeyError:
            logging.getLogger("DSLink").debug("Unknown rid %s" % rid)


class Configuration:
    """ Provides configuration to the DSLink. """

    def __init__(self, name, broker, responder=False, requester=False):
        self.name = name
        self.broker = broker
        self.responder = responder
        self.requester = requester
