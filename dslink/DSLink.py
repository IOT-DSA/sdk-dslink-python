import argparse
import base64
import hashlib
import logging
from urlparse import urlparse

import signal
from twisted.internet import reactor

from dslink.Crypto import Keypair
from dslink.Handshake import Handshake
from dslink.Requester import Requester
from dslink.Responder import Responder
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
        self.active = False
        self.needs_auth = False

        # DSLink Configuration
        self.config = config
        self.server_config = None

        # Logger setup
        self.logger = self.create_logger("DSLink", self.config.log_level)
        self.logger.info("Starting DSLink")

        def stop(*args):
            reactor.stop()

        signal.signal(signal.SIGINT, stop)

        # Requester and Responder setup
        if self.config.requester:
            self.requester = Requester(self)
        if self.config.responder:
            self.responder = Responder(self)
            self.responder.start()

        # DSLink setup
        self.keypair = Keypair(self.config.keypair_path)
        self.handshake = Handshake(self, self.keypair)
        self.handshake.run_handshake()
        self.dsid = self.handshake.get_dsid()

        # Connection setup
        self.wsp = None
        self.websocket = WebSocket(self)

        self.call_later(1, self.start)

        self.logger.info("Started DSLink")
        self.logger.debug("Starting reactor")
        reactor.run(installSignalHandlers=False)

    def start(self):
        """
        Called once the DSLink is initialized and connected.
        Override this rather than the constructor.
        """
        pass

    # noinspection PyMethodMayBeStatic
    def get_default_nodes(self, super_root):
        """
        Create the default Node structure in this, override it.
        :param super_root: Super Root.
        :return: Super Root with default Node structure.
        """
        return super_root

    def get_auth(self):
        """
        Get auth parameter for connection.
        :return: Auth parameter.
        """
        auth = str(self.server_config["salt"]) + self.shared_secret
        auth = base64.urlsafe_b64encode(hashlib.sha256(auth).digest()).decode("utf-8").replace("=", "")
        return auth

    def get_url(self):
        """
        Get full WebSocket URL.
        :return: WebSocket URL.
        """
        websocket_uri = self.config.broker[:-5].replace("http", "ws") + "/ws?dsId=%s" % self.dsid
        if self.needs_auth:
            websocket_uri += "&auth=%s" % self.get_auth()
        if self.config.token is not None:
            websocket_uri += "&token=%s" % self.config.token
        url = urlparse(websocket_uri)
        if url.port is None:
            port = 80
        else:
            port = url.port
        return websocket_uri, url, port

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

    @staticmethod
    def call_later(delay, call, *args, **kw):
        """
        Call function later.
        :param delay: Seconds to delay.
        :param call: Method to call.
        :param args: Arguments.
        :return: DelayedCall instance.
        """
        return reactor.callLater(delay, call, *args, **kw)


class Configuration:
    """
    Provides configuration to the DSLink.
    """

    def __init__(self, name, responder=False, requester=False, ping_time=30, keypair_path=".keys",
                 nodes_path="nodes.json", no_save_nodes=False):
        """
        Object that contains configuration for the DSLink.
        :param name: DSLink name.
        :param responder: True if responder, default is False.
        :param requester: True if requester, default is False.
        :param ping_time: Time between pings, default is 30.
        :param keypair_path: Path to save keypair, default is ".keys".
        :param nodes_path: Path to save nodes.json, default is "nodes.json".
        :param no_save_nodes: Don't use nodes.json, default is False.
        """
        if not responder and not requester:
            raise ValueError("DSLink is neither responder nor requester.")
        parser = argparse.ArgumentParser()
        parser.add_argument("--broker", default="http://localhost:8080/conn")
        parser.add_argument("--log", default="info")
        parser.add_argument("--token")
        args = parser.parse_args()
        self.name = name
        self.broker = args.broker
        self.log_level = args.log.lower()
        self.token = args.token
        self.responder = responder
        self.requester = requester
        self.ping_time = ping_time
        self.keypair_path = keypair_path
        self.nodes_path = nodes_path
        self.no_save_nodes = no_save_nodes

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
