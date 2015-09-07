import base64
import hashlib
import json

from autobahn.twisted.websocket import WebSocketClientProtocol, connectWS, WebSocketClientFactory
from twisted.internet import reactor
from dslink.Node import Node

from dslink.Request import Request
from dslink.Response import Response


# TODO(logangorence): Switch to asyncio
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
    def __init__(self):
        super().__init__()
        self.msg = 0
        self.superRoot = Node(None, None)

    def sendPingMsg(self):
        print("DEBUG Ping")
        self.sendMessage({})
        reactor.callLater(30, self.sendPingMsg)

    def onOpen(self):
        print("Open!")
        self.sendPingMsg()

    def onClose(self, wasClean, code, reason):
        print("Closed!")

    def onMessage(self, payload, isBinary):
        i = json.loads(payload.decode("utf-8"))
        print("Recv:", i)
        m = {}
        ack = False
        if "requests" in i and len(i["requests"]) > 0:
            ack = True
            self.handleRequests(i["requests"])
        if "responses" in i and len(i["responses"]) > 0:
            ack = True
            self.handleResponses(i["responses"])
        # if ack:
        if "msg" in i:
            m["ack"] = i["msg"]
        self.sendMessage(m)

    def handleRequests(self, requests):
        for request in requests:
            Request(request)

    def handleResponse(self, responses):
        for response in responses:
            Response(response)

    def sendMessage(self, payload, isBinary=False, fragmentSize=None, sync=False, doNotCompress=False):
        payload["msg"] = self.msg
        self.msg += 1
        print("Sent:", payload)
        payload = json.dumps(payload).encode("utf-8")
        super().sendMessage(payload, isBinary, fragmentSize, sync, doNotCompress)
