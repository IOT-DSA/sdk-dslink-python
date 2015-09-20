import base64
import logging

from dslink.Crypto import Keypair
from dslink.Handshake import Handshake
from dslink.Node import Node
from dslink.WebSocket import WebSocket


class DSLink:
    def __init__(self, config):
        # Temporary Node tree
        self.super_root = Node("", None)
        self.super_root.link = self
        self.super_root.add_child(Node("TestValue", self.super_root))
        self.super_root.add_child(Node("TestNode", self.super_root))
        self.super_root.get("/TestValue").set_value(1)
        self.super_root.get("/TestValue").config["$type"] = "number"

        # Logger setup
        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        self.ch = logging.StreamHandler()
        self.ch.setFormatter(formatter)
        self.ch.setLevel(logging.DEBUG)
        self.logger = logging.getLogger("DSLink")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.ch)
        self.logger.info("Starting DSLink...")

        # Subscription setup
        self.subman = SubscriptionManager()

        # DSLink setup
        self.config = config
        self.keypair = Keypair()
        self.handshake = Handshake(config.name, config.broker, self.keypair, config.responder, config.requester)
        self.server_config = self.handshake.run_handshake()
        self.salt = self.server_config["salt"]
        self.dsid = self.handshake.get_dsid()
        self.shared_secret = self.keypair.keypair.get_ecdh_key(base64.urlsafe_b64decode(self.add_padding(self.server_config["tempKey"])))

        # Connection setup
        self.websocket = WebSocket(self)

    @staticmethod
    def add_padding(string):
        while len(string) % 4 != 0:
            string += "="
        return string


class SubscriptionManager:
    def __init__(self):
        self.subscriptions = {}

    def subscribe(self, node, sid):
        self.subscriptions[sid] = node
        self.subscriptions[sid].subscribers.append(sid)

    def unsubscribe(self, sid):
        self.subscriptions[sid].subscribers.remove(sid)
        self.subscriptions[sid] = None


class Configuration:
    def __init__(self, name, broker, responder=False, requester=False):
        self.name = name
        self.broker = broker
        self.responder = responder
        self.requester = requester
