import base64
import hashlib
import logging

from .Crypto import KeyPairHandler


class Configuration:
    def __init__(self, dslink, options):
        self.broker = options.broker
        self.log_level = getattr(logging, options.log.upper(), logging.NOTSET)
        self.token = options.token
        self.crypto = KeyPairHandler(".keys")
        self.is_responder = dslink.is_responder
        self.is_requester = dslink.is_requester
        self.ds_id = dslink.name + "-" + self.crypto.b64

        self.format = "json"
        self.shared_secret = None
        self.temp_key = None
        self.server_config = None
        self.auth = None

    @staticmethod
    def token_hash(ds_id, token):
        pad = 16
        if token is not None and len(token) > pad:
            token_id = token[:pad]
            hash_str = base64.urlsafe_b64encode(hashlib.sha256((ds_id + token)).digest())
            return "&token=" + token_id + hash_str.decode('utf-8').replace('=', '')
        else:
            return None

    def get_ws_uri(self):
        websocket_uri = self.broker[:-5]
        if websocket_uri.startswith("https"):
            websocket_uri = websocket_uri.replace("https", "wss")
        elif websocket_uri.startswith("http"):
            websocket_uri = websocket_uri.replace("http", "ws")
        else:
            raise Exception("Unrecognized protocol in URL: " % websocket_uri)
        websocket_uri += "/ws?dsId=%s&format=%s" % (self.ds_id, self.format)
        if self.auth is not None:
            websocket_uri += "&auth=%s" % self.auth
        token = self.token_hash(self.ds_id, self.token)
        if token is not None:
            websocket_uri += token
        return websocket_uri
