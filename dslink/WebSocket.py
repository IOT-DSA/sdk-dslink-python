import base64
import hashlib
import json
from threading import Timer
from urllib.parse import urlparse

import asyncio
from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory

from dslink.Request import Request
from dslink.Response import Response


class WebSocket:
    def __init__(self, link):
        self.link = link
        self.auth = bytes(link.salt, "utf-8") + link.shared_secret
        self.auth = base64.urlsafe_b64encode(hashlib.sha256(self.auth).digest()).decode("utf-8").replace("=", "")

        # TODO(logangorence): Properly strip and replace with WebSocket path
        websocket_uri = link.config.broker[:-5].replace("http", "ws") + "/ws" + "?dsId=" + link.dsid + "&auth=" + self.auth
        url = urlparse(websocket_uri)
        factory = WebSocketClientFactory(websocket_uri)
        factory.protocol = DSAWebSocket
        loop = asyncio.get_event_loop()
        coro = loop.create_connection(factory, host=url.hostname, port=url.port)
        loop.run_until_complete(coro)
        loop.run_forever()
        loop.close()


class DSAWebSocket(WebSocketClientProtocol):
    def __init__(self):
        super().__init__()
        self.msg = 0

    def sendPingMsg(self):
        print("DEBUG Ping")
        self.sendMessage({})
        i = Timer(30, self.sendPingMsg, ())
        i.start()

    def onOpen(self):
        self.sendPingMsg()

    def onClose(self, wasClean, code, reason):
        print("WebSocket was closed.")

    def onMessage(self, payload, isBinary):
        i = json.loads(payload.decode("utf-8"))
        print("Recv:", i)
        m = {}
        ack = False
        if "requests" in i and len(i["requests"]) > 0:
            ack = True
            m["responses"] = self.handleRequests(i["requests"])
        if "responses" in i and len(i["responses"]) > 0:
            ack = True
            self.handleResponses(i["responses"])
        if ack:
            m["ack"] = i["msg"]
            self.sendMessage(m)

    def handleRequests(self, requests):
        i = []
        for request in requests:
            i.append(Request(request).process().get_stream())
        return i

    def handleResponse(self, responses):
        for response in responses:
            Response(response)

    def sendMessage(self, payload, isBinary=False, fragmentSize=None, sync=False, doNotCompress=False):
        payload["msg"] = self.msg
        self.msg += 1
        payload = json.dumps(payload)
        print("Sent:", payload)
        payload = payload.encode("utf-8")
        super().sendMessage(payload, isBinary, fragmentSize, sync, doNotCompress)
