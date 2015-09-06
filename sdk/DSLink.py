from sdk.Crypto import Keypair
from sdk.Handshake import Handshake
from sdk.WebSocket import WebSocket

import base64


class DSLink:
    def __init__(self, config):
        self.keypair = Keypair()
        self.handshake = Handshake(config.name, config.broker, self.keypair, config.responder, config.requester)
        self.server_config = self.handshake.run_handshake()
        self.shared_secret = self.keypair.keypair.get_ecdh_key(base64.urlsafe_b64decode(self.add_padding(self.server_config["tempKey"])))
        self.websocket = WebSocket(self.server_config["salt"], self.shared_secret, config.broker, self.handshake.get_dsid())

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
