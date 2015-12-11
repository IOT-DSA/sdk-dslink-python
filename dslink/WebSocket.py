import json
import logging

from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
from autobahn.websocket.protocol import parseWsUrl
from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory

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
        websocket_uri, url, port = link.get_url()

        DSAWebSocket.link = link
        factory = DSAWebSocketFactory(websocket_uri, link)
        factory.protocol = DSAWebSocket

        link.logger.debug("Connecting WebSocket to %s" % websocket_uri)
        reactor.connectTCP(url.hostname, port, factory)


class DSAWebSocketFactory(WebSocketClientFactory, ReconnectingClientFactory):
    def __init__(self, websocket_uri, link):
        super(DSAWebSocketFactory, self).__init__(websocket_uri)
        self.link = link
    
    def clientConnectionFailed(self, connector, reason):
        print("Failed to connect, retrying...")
        self.link.handshake.run_handshake()
        self.reset_url()
        self.retry(connector)

    def clientConnectionLost(self, connector, unused_reason):
        print("Connection lost, retrying...")
        self.link.handshake.run_handshake()
        self.reset_url()
        self.retry(connector)

    def reset_url(self):
        websocket_uri, url, port = self.link.get_url()
        self.url = websocket_uri
        (self.isSecure, self.host, self.port, self.resource, self.path, self.params) = parseWsUrl(websocket_uri)


class DSAWebSocket(WebSocketClientProtocol):
    """
    Autobahn implementation for DSA communications.
    """
    def __init__(self):
        """
            Constructor for DSAWebSocket.
            """
        super(DSAWebSocket, self).__init__()
        self.msg = 0
        self.logger = logging.getLogger("DSLink")
        self.link = DSAWebSocket.link
        self.link.wsp = self

    def sendPingMsg(self):
        """
        Send a blank object for a ping.
        """
        self.logger.debug("Sent ping")
        # noinspection PyTypeChecker
        self.sendMessage({})
        reactor.callLater(self.link.config.ping_time, self.sendPingMsg)

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
            if response["rid"] is 0:
                for update in response["updates"]:
                    sid = update[0]
                    val = update[1]
                    time = update[2]
                    self.link.requester.subscription_manager.run_callback(sid, val, time)
            elif response["rid"] in self.link.requester.request_manager.requests:
                self.link.requester.request_manager.invoke_request(response["rid"], response)

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
        super(DSAWebSocket, self).sendMessage(payload, isBinary, fragmentSize, sync, doNotCompress)
