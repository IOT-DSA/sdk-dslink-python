import json

import requests


class Handshake:
    """
    Class that handles the DSA Handshake.
    """

    def __init__(self, link, keypair):
        self.link = link
        self.keypair = keypair

    def get_dsid(self):
        return self.link.config.name + "-" + self.keypair.b64

    def get_publickey(self):
        return self.keypair.encoded_public

    def get_json(self):
        return json.dumps({
            "publicKey": self.get_publickey(),
            "isRequester": self.link.config.requester,
            "isResponder": self.link.config.responder,
            "version": "1.1.1"
        }, sort_keys=True)

    def run_handshake(self):
        url = self.link.config.broker + "?dsId=%s" % self.get_dsid()
        if self.link.config.token is not None:
            url += "&token=%s" % self.link.config.token
        self.link.logger.debug("Running handshake on %s" % url)
        response = requests.post(url, data=self.get_json())
        if response.status_code is not 200:
            self.link.logger.error("Non-200 status code")
            exit(1)
        return json.loads(response.text)
