import base64
import hashlib
import json
import logging
import requests

from .Util import base64_add_padding
from .Serializers import serializers


class Handshake:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def get_handshake_request(self):
        serializer_names = []
        for key in serializers:
            serializer_names.append(key)
        return json.dumps({
            "publicKey": self.config.crypto.encoded_public,
            "isRequester": self.config.is_requester,
            "isResponder": self.config.is_responder,
            "version": "1.1.2",
            # "formats": (serializer_names if self.link.config.comm_format == "" else [self.link.config.comm_format])
            # TODO:
            "formats": ["json"]
        }, sort_keys=True)

    def run_handshake(self):
        url = self.config.broker + "?dsId=%s" % self.config.ds_id
        token = self.config.token_hash(self.config.ds_id, self.config.token)
        if token is not None:
            url += token
        self.logger.debug("Running handshake on %s" % url)
        try:
            handshake_body = self.get_handshake_request()
            self.logger.debug("Handshake body: %s" % handshake_body)
            response = requests.post(url, data=handshake_body, verify=False)
            if response.status_code is 200:
                server_config = json.loads(response.text)
                self.config.format = server_config["format"]
                self.config.server_config = server_config
                self.logger.debug("Server handshake body: %s" % json.dumps(server_config))
                if "tempKey" in server_config:
                    self.config.temp_key = self.config.crypto.keypair.decode_tempkey(
                        base64.urlsafe_b64decode(base64_add_padding(server_config["tempKey"]).encode("utf-8")))
                    self.config.shared_secret = self.config.crypto.keypair.generate_shared_secret(self.config.temp_key)
                    salt_shared_secret = server_config["salt"].encode("utf-8", "ignore") + self.config.shared_secret
                    self.config.auth = base64.urlsafe_b64encode(
                        hashlib.sha256(salt_shared_secret).digest()
                    ).decode("utf-8").replace("=", "")
                else:
                    # Reset auth state
                    self.config.temp_key = None
                    self.config.shared_secret = None
                    self.config.auth = None
                return True
            else:
                # It's likely that our protocol is messed up, raise an exception to die
                raise Exception("Handshake returned non-200 code: %s" % response.status_code)
        except requests.exceptions.ConnectionError as e:
            self.link.logger.error("DSLink occurred a ConnectionError: %s" % e)
            return False
