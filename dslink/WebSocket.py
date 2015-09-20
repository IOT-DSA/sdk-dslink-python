import base64
import hashlib
import json
import logging
from threading import Timer, Thread
from urllib.parse import urlparse

import asyncio
from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory

from dslink.Request import Request
from dslink.Response import Response


class WebSocket:
    def __init__(self, link):
        self.link = link
        self.factory = None
        self.auth = bytes(link.salt, "utf-8") + link.shared_secret
        self.auth = base64.urlsafe_b64encode(hashlib.sha256(self.auth).digest()).decode("utf-8").replace("=", "")

        # TODO(logangorence): Properly strip and replace with WebSocket path
        self.websocket_uri = link.config.broker[:-5].replace("http", "ws") + "/ws" + "?dsId=" + link.dsid + "&auth=" + self.auth
        self.url = urlparse(self.websocket_uri)

        DSAWebSocket.link = link

        loop = asyncio.get_event_loop()
        t = Thread(target=self.start_ws, args=(loop,))
        t.start()

    def start_ws(self, loop):
        asyncio.set_event_loop(loop)
        self.factory = WebSocketClientFactory(self.websocket_uri)
        self.factory.protocol = DSAWebSocket
        self.factory.ws = self
        coro = loop.create_connection(self.factory, host=self.url.hostname, port=self.url.port)
        loop.run_until_complete(coro)
        loop.run_forever()
        loop.close()


class DSAWebSocket(WebSocketClientProtocol):
    def __init__(self):
        super().__init__()
        self.msg = 0
        self.logger = logging.getLogger("DSLink")
        self.link = DSAWebSocket.link
        self.link.wsp = self

    def sendPingMsg(self):
        self.logger.debug("Sent ping")
        self.sendMessage({})
        i = Timer(30, self.sendPingMsg, ())
        i.start()

    def onOpen(self):
        self.logger.info("WebSocket Open")
        self.sendPingMsg()

    def onClose(self, wasClean, code, reason):
        self.logger.info("WebSocket Closed")

    def onMessage(self, payload, isBinary):
        self.logger.debug("Received data: %s" % payload.decode("utf-8"))
        i = json.loads(payload.decode("utf-8"))
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
            i.append(Request(request, self.link).process().get_stream())
        return i

    def handleResponse(self, responses):
        for response in responses:
            Response(response)

    def sendMessage(self, payload, isBinary=False, fragmentSize=None, sync=False, doNotCompress=False):
        payload["msg"] = self.msg
        self.msg += 1
        payload = json.dumps(payload)
        self.logger.debug("Sent data: %s" % payload)
        payload = payload.encode("utf-8")
        super().sendMessage(payload, isBinary, fragmentSize, sync, doNotCompress)
