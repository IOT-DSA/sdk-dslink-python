import base64
import hashlib
import json

from twisted.internet import reactor

from autobahn.twisted.websocket import WebSocketClientProtocol, connectWS, WebSocketClientFactory

class WebSocket:
    def __init__(self, salt, shared_secret, broker, dsid):
        self.auth = bytes(salt, "utf-8") + shared_secret
        self.auth = base64.urlsafe_b64encode(hashlib.sha256(self.auth).digest()).decode("utf-8").replace("=", "")

        # TODO(logangorence): Properly strip and replace with WebSocket path
        websocket_uri = broker[:-5].replace("http", "ws") + "/ws" + "?dsId=" + dsid + "&auth=" + self.auth
        factory = WebSocketClientFactory(websocket_uri)
        factory.protocol = DSAWebSocket
        connectWS(factory)

        reactor.run()


class DSAWebSocket(WebSocketClientProtocol):
    def onOpen(self):
        print("Open!")

    def onClose(self, wasClean, code, reason):
        print("Closed!")

    def onMessage(self, payload, isBinary):
        print(json.loads(payload.decode("utf-8")))
