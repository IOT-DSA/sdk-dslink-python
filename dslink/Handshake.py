import json

import requests


class Handshake:
    def __init__(self, name, broker, keypair, responder=False, requester=False):
        self.name = name
        self.broker = broker
        self.keypair = keypair
        self.responder = responder
        self.requester = requester

    def get_dsid(self):
        return self.name + "-" + self.keypair.b64

    def get_publickey(self):
        return self.keypair.encoded_public

    def get_json(self):
        return json.dumps({
            "publicKey": self.get_publickey(),
            "isRequester": self.requester,
            "isResponder": self.responder,
            "version": "1.1.1"
        })

    def run_handshake(self):
        # TODO(logangorence): Handle ConnectionRefusedError
        response = requests.post(self.broker + "?dsId=" + self.get_dsid(), data=self.get_json())
        # TODO(logangorence): Handle non-200 error responses and empty responses
        return json.loads(response.text)
