import argparse
import base64
import hashlib
import logging
import signal
from twisted.internet import reactor
try:  # python v2 first, v3+ upon exception:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from .FileStorage import FileStorage
from .Crypto import Crypto
from .Handshake import Handshake
from .Requester import Requester
from .Responder import Responder
from .WebSocket import WebSocket


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
        self.shared_secret = ""

        # DSLink Configuration
        self.config = config
        self.server_config = None
        self.storage = FileStorage(self)

        # Logger setup
        self.logger = self.create_logger("DSLink", self.config.log_level)
        self.logger.info("Starting DSLink")

        if not self.config.disable_signals:
            # Signal setup
            signal.signal(signal.SIGINT, self.stop)
            signal.signal(signal.SIGTERM, self.stop)

        # Requester and Responder setup
        if self.config.requester:
            self.requester = Requester(self)
        if self.config.responder:
            self.responder = Responder(self)
            self.responder.start()

        # DSLink setup
        self.keypair = Crypto(self.config.keypair_path)
        self.handshake = Handshake(self, self.keypair)
        self.handshake.run_handshake()
        self.dsid = self.handshake.get_dsid()

        # Connection setup
        self.wsp = None
        self.websocket = WebSocket(self)

        self.start()

        self.logger.info("Started DSLink")
        self.logger.debug("Starting reactor")
        if not self.config.disable_signals:
            reactor.run(installSignalHandlers=False)
        else:
            reactor.run()

    def start(self):
        """
        Called once the DSLink is initialized. Used to initialize
        your own code.
        """
        pass

    def on_connected(self):
        """
        Called when the DSLink connects to the broker.
        """
        pass

    def on_disconnected(self):
        """
        Called when the DSLink disconnects from the broker.
        """
        pass

    # noinspection PyUnresolvedReferences
    def stop(self, *args):
        """
        Called when the DSLink is going to stop.
        :param args: Signal arguments.
        """
        if self.wsp is not None:
            reactor.callFromThread(self.wsp.sendClose)
        reactor.removeAll()
        reactor.iterate()
        reactor.stop()

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
        auth = self.server_config["salt"].encode("utf-8", "ignore") + self.shared_secret
        # Digest with SHA256, and then base64 the result.
        return base64.urlsafe_b64encode(hashlib.sha256(auth).digest()).decode("utf-8").replace("=", "")

    def get_url(self):
        """
        Get full WebSocket URL.
        :return: WebSocket URL.
        """
        websocket_uri = self.config.broker[:-5]
        if websocket_uri.startswith("https"):
            websocket_uri = websocket_uri.replace("https", "wss")
        elif websocket_uri.startswith("http"):
            websocket_uri = websocket_uri.replace("http", "ws")
        else:
            raise Exception("Unrecognized protocol in URL: " % websocket_uri)
        websocket_uri += "/ws?dsId=%s&format=%s" % (self.dsid, self.config.comm_format)
        if self.needs_auth:
            websocket_uri += "&auth=%s" % self.get_auth()
        token = self.config.token_hash(self.dsid, self.config.token)
        if token is not None:
            websocket_uri += token
        return websocket_uri

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
                 nodes_path="nodes.json", no_save_nodes=False, disable_signals=False, comm_format=""):
        """
        Object that contains configuration for the DSLink.
        :param name: DSLink name.
        :param responder: True if responder, default is False.
        :param requester: True if requester, default is False.
        :param ping_time: Time between pings, default is 30.
        :param keypair_path: Path to save keypair, default is ".keys".
        :param nodes_path: Path to save nodes.json, default is "nodes.json".
        :param no_save_nodes: Don't use nodes.json, default is False.
        :param disable_signals: Disable the installation of Python signals.
        :param comm_format: Changes default communications format, usually "json" or "msgpack".
        """
        if not responder and not requester:
            raise ValueError("DSLink must be either a responder or requester")
        parser = argparse.ArgumentParser()
        parser.add_argument("--broker", default="http://localhost:8080/conn")
        parser.add_argument("--log", default="info")
        parser.add_argument("--token")
        args = parser.parse_args()
        self.name = name
        self.dsid = None
        self.broker = args.broker
        self.log_level = getattr(logging, args.log.upper(), logging.NOTSET)
        self.token = args.token
        self.responder = responder
        self.requester = requester
        self.ping_time = ping_time
        self.keypair_path = keypair_path
        self.nodes_path = nodes_path
        self.no_save_nodes = no_save_nodes
        self.disable_signals = disable_signals
        self.comm_format = comm_format

    @staticmethod
    def token_hash(dsid, token):
        pad = 16
        if token is not None and len(token) > pad:
            token_id = token[:pad]
            hash_str = base64.urlsafe_b64encode(hashlib.sha256((dsid + token)).digest())
            return "&token=" + token_id + hash_str.decode('utf-8').replace('=', '')
        else:
            return None
