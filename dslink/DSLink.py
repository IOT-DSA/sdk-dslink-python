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
        # DSLink Configuration
        self.config = config

        # Temporary Node tree
        self.super_root = Node("", None)
        self.super_root.link = self

        # Logger setup
        self.logger = self.create_logger("DSLink", self.config.log_level)
        self.logger.info("Starting DSLink")

        # Subscription/stream setup
        self.subman = SubscriptionManager()
        self.strman = StreamManager()

        # DSLink setup
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

        self.logger.info("Started DSLink")

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
        self.subscriptions = {}

    def subscribe(self, node, sid):
        self.subscriptions[sid] = node
        self.subscriptions[sid].subscribers.append(sid)

    def unsubscribe(self, sid):
        try:
            self.subscriptions[sid].subscribers.remove(sid)
            self.subscriptions[sid] = None
        except KeyError:
            logging.getLogger("DSlink").debug("Unknown sid %s" % sid)


class StreamManager:
    """
    Manages streams for Nodes.
    """

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
    """
    Provides configuration to the DSLink.
    """

    def __init__(self, name, responder=False, requester=False, ping_time=30):
        """
        Object that contains configuration for the DSLink.
        :param name: DSLink name.
        :param responder: True if acts as responder.
        :param requester: True if acts as requester.
        :param ping_time: Time between pings, default is 30.
        """
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
