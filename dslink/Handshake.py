import json

import requests


class Handshake:
    """
    Class that handles the DSA Handshake.
    """

    def __init__(self, link, name, broker, keypair, responder=False, requester=False):
        self.link = link
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
        }, sort_keys=True)

    def run_handshake(self):
        response = requests.post(self.broker + "?dsId=" + self.get_dsid(), data=self.get_json())
        if response.status_code is not 200:
            self.link.logger.error("Non-200 status code")
            exit(1)
        return json.loads(response.text)
