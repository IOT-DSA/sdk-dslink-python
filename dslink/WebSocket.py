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
    """
    Class to handle WebSocket.
    """

    def __init__(self, link):
        """
        WebSocket Constructor.
        :param link: DSLink instance.
        """
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
        """
        Start the WebSocket in a separate thread.
        :param loop: asyncio loop
        """
        asyncio.set_event_loop(loop)
        self.factory = WebSocketClientFactory(self.websocket_uri)
        self.factory.protocol = DSAWebSocket
        coro = loop.create_connection(self.factory, host=self.url.hostname, port=self.url.port)
        loop.run_until_complete(coro)
        loop.run_forever()
        loop.close()


class DSAWebSocket(WebSocketClientProtocol):
    """
    Autobahn implementation for DSA communications.
    """

    def __init__(self):
        """
        Constructor for DSAWebSocket.
        """
        super().__init__()
        self.msg = 0
        self.logger = logging.getLogger("DSLink")
        # noinspection PyUnresolvedReferences
        self.link = DSAWebSocket.link
        self.link.wsp = self

    def sendPingMsg(self):
        """
        Send a blank object for a ping.
        """
        self.logger.debug("Sent ping")
        # noinspection PyTypeChecker
        self.sendMessage({})
        i = Timer(self.link.config.ping_time, self.sendPingMsg, ())
        i.start()

    def onOpen(self):
        """
        WebSocket open event.
        """
        self.link.active = True
        self.logger.info("WebSocket Connection Established")
        self.sendPingMsg()

    def onClose(self, wasClean, code, reason):
        """
        WebSocket close event.
        :param wasClean: True if the close was clean.
        :param code: Close code.
        :param reason: Close reason.
        """
        self.link.active = False
        self.logger.info("WebSocket Connection Lost")
        # TODO(logangorence): Attempt reconnection

    def onMessage(self, payload, isBinary):
        """
        WebSocket message event.
        :param payload: Data to send.
        :param isBinary: True if the message is binary.
        """
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
            # noinspection PyTypeChecker
            self.sendMessage(m)

    def handleRequests(self, requests):
        """
        Handle incoming requests.
        :param requests: List of requests.
        :return: Outgoing responses.
        """
        i = []
        for request in requests:
            i.append(Request(request, self.link).process().get_stream())
        return i

    def handleResponses(self, responses):
        """
        Handle incoming responses.
        :param responses: List of responses.
        """
        for response in responses:
            Response(response)
            if response["rid"] in self.link.reqman.requests:
                self.link.reqman.invoke_request(response["rid"], response)

    def sendMessage(self, payload, isBinary=False, fragmentSize=None, sync=False, doNotCompress=False):
        """
        Send a message over the WebSocket.
        :param payload: Message to send.
        """
        payload["msg"] = self.msg
        self.msg += 1
        payload = json.dumps(payload, sort_keys=True)
        self.logger.debug("Sent data: %s" % payload)
        payload = payload.encode("utf-8")
        super().sendMessage(payload, isBinary, fragmentSize, sync, doNotCompress)
