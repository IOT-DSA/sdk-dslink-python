import base64
import json
import time
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
        keep_trying = True
        cooldown = 1
        while keep_trying:
            try:
                response = requests.post(url, data=self.get_json())
                if response.status_code is 200:
                    keep_trying = False
                    continue
            except requests.exceptions.ConnectionError:
                pass
            self.link.logger.info("Failed to connect to %s" % url)
            time.sleep(cooldown)
            if cooldown <= 60:
                cooldown += 1
        # noinspection PyUnboundLocalVariable
        self.link.server_config = json.loads(response.text)
        if "tempKey" in self.link.server_config:
            self.link.needs_auth = True
            self.link.shared_secret = self.keypair.keypair.get_ecdh_key(
                base64.urlsafe_b64decode(self.link.add_padding(self.link.server_config["tempKey"]).encode("utf-8")))
