from .Util import base64_add_padding

import base64
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

    def get_handshake_request(self):
        serializer_names = []
        from dslink.Serializers import serializers
        for key in serializers:
            serializer_names.append(key)
        return json.dumps({
            "publicKey": self.get_publickey(),
            "isRequester": self.link.config.requester,
            "isResponder": self.link.config.responder,
            "version": "1.1.2",
            "formats": (serializer_names if self.link.config.comm_format == "" else [self.link.config.comm_format])
        }, sort_keys=True)

    def run_handshake(self):
        url = self.link.config.broker + "?dsId=%s" % self.get_dsid()
        token = self.link.config.token_hash(self.get_dsid(), self.link.config.token)
        if token is not None:
            url += token
        self.link.logger.debug("Running handshake on %s" % url)
        try:
            handshake_body = self.get_handshake_request()
            self.link.logger.debug("Handshake body: %s" % handshake_body)
            response = requests.post(url, data=handshake_body)
            if response.status_code is 200:
                server_config = json.loads(response.text)
                self.link.server_config = server_config
                if server_config["format"] is not None:
                    self.link.config.comm_format = server_config["format"]
                if "tempKey" in self.link.server_config:
                    self.link.needs_auth = True
                    self.link.shared_secret = self.keypair.keypair.get_ecdh_key(
                        base64.urlsafe_b64decode(base64_add_padding(self.link.server_config["tempKey"]).encode("utf-8")))
                return True
            else:
                raise Exception("Handshake returned non-200 code: %s" % response.status_code)
        except requests.exceptions.ConnectionError as conn:
            raise Exception("Unknown connection error while handshaking")
        #self.link.logger.info("Failed to handshake %s" % url)
        #return False
