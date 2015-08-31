import base64
import hashlib
import json
import os.path
import pickle

import pyelliptic
import requests


class Handshake:
    def __init__(self, name, responder=False, requester=False):
        self.name = name
        self.responder = responder
        self.requester = requester
        self.keypair = Keypair()

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
        response = requests.post("http://localhost:8080/conn?dsId=" + self.get_dsid(), data=self.get_json())

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
