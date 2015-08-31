import base64
import hashlib
import json
import requests

import pyelliptic


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
        requests.post("http://localhost:8080/conn?dsId=" + self.get_dsid(), data=self.get_json())

class Keypair:
    def __init__(self):
        self.keypair = pyelliptic.ECC(curve="prime256v1")
        sha = hashlib.sha256(self.keypair.get_pubkey())
        self.b64 = base64.urlsafe_b64encode(sha.digest()).decode("utf-8").replace("=", "")
        self.encoded_public = base64.urlsafe_b64encode(self.keypair.get_pubkey()).decode("utf-8").replace("=", "")
