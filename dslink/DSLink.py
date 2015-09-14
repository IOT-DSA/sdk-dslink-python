from dslink.Crypto import Keypair
from dslink.Handshake import Handshake
from dslink.Node import Node
from dslink.WebSocket import WebSocket

import base64


class DSLink:
    def __init__(self, config):
        self.config = config
        self.keypair = Keypair()
        self.handshake = Handshake(config.name, config.broker, self.keypair, config.responder, config.requester)
        self.server_config = self.handshake.run_handshake()
        self.salt = self.server_config["salt"]
        self.dsid = self.handshake.get_dsid()
        self.shared_secret = self.keypair.keypair.get_ecdh_key(base64.urlsafe_b64decode(self.add_padding(self.server_config["tempKey"])))
        self.super_root = Node(None, None)
        self.websocket = WebSocket(self)

    @staticmethod
    def add_padding(string):
        while len(string) % 4 != 0:
            string += "="
        return string


class Configuration:
    def __init__(self, name, broker, responder=False, requester=False):
        self.name = name
        self.broker = broker
        self.responder = responder
        self.requester = requester
