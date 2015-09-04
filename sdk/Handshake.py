import base64
import hashlib
import binascii
import json
import os.path
import pickle

from autobahn.twisted.websocket import WebSocketClientProtocol, connectWS, WebSocketClientFactory
import pyelliptic
import requests
from twisted.internet import reactor


class Handshake:
    def __init__(self, name, broker, responder=False, requester=False):
        self.name = name
        self.broker = broker
        self.responder = responder
        self.requester = requester
        self.keypair = Keypair()
        self.run_handshake()
        self.start_websocket()

    def get_dsid(self):
        return self.name + "-" + self.keypair.b64

    def get_publickey(self):
        return self.keypair.encoded_public

    def get_json(self):
        return json.dumps({
            "publicKey": self.get_publickey(),
            "isRequester": self.requester,
            "isResponder": self.responder,
            "version": "1.0.4"
        })

    def run_handshake(self):
        response = requests.post(self.broker + "?dsId=" + self.get_dsid(), data=self.get_json())
        # TODO(logangorence): Handle non-200 error responses and empty responses
        self.server_config = json.loads(response.text)
        self.shared_secret = self.keypair.keypair.get_ecdh_key(base64.urlsafe_b64decode(self.add_padding(self.server_config["tempKey"])))

    def start_websocket(self):
        print(len(self.shared_secret))

        print(self.shared_secret)
        dsAuth = binascii.hexlify(bytes(self.server_config["salt"], "utf-8")) + self.shared_secret
        dsAuth = base64.urlsafe_b64encode(hashlib.sha256(dsAuth).digest()).decode("utf-8").replace("=", "")

        # TODO(logangorence): Properly strip and replace with WebSocket path
        websocket_uri = self.broker[:-5].replace("http", "ws") + self.server_config["wsUri"] + "?auth=" + dsAuth + "&dsId=" + self.get_dsid()
        print(websocket_uri)
        factory = WebSocketClientFactory(websocket_uri)
        factory.protocol = DSAWebSocket
        connectWS(factory)

        reactor.run()

    @staticmethod
    def add_padding(string):
        while len(string) % 4 != 0:
            string += "="
        return string

class Keypair:
    def __init__(self):
        self.keypair = None
        if not os.path.isfile(".keys"):
            self.generate_key()
            self.save_keys()
        else:
            self.load_keys()
        sha = hashlib.sha256(self.keypair.get_pubkey())
        self.b64 = base64.urlsafe_b64encode(sha.digest()).decode("utf-8").replace("=", "")
        self.encoded_public = base64.urlsafe_b64encode(self.keypair.get_pubkey()).decode("utf-8").replace("=", "")

    def generate_key(self):
        self.keypair = pyelliptic.ECC(curve="prime256v1")

    def load_keys(self):
        file = open(".keys", "rb")
        keys = pickle.load(file)
        self.keypair = pyelliptic.ECC(curve="prime256v1",
                                      pubkey_x=keys["pubkey_x"],
                                      pubkey_y=keys["pubkey_y"],
                                      raw_privkey=keys["privkey"])

    def save_keys(self):
        file = open(".keys", "wb")
        pickle.dump({
            "pubkey_x": self.keypair.pubkey_x,
            "pubkey_y": self.keypair.pubkey_y,
            "privkey": self.keypair.privkey
        }, file)

    def get_ecdh_key(self, pubkey):
        self.keypair.get_ecdh_key(pubkey.encode("utf-8"))

class DSAWebSocket(WebSocketClientProtocol):
    def onOpen(self):
        print("Open!")

    def onClose(self, wasClean, code, reason):
        print("Closed!")

    def onMessage(self, payload, isBinary):
        print(payload)
