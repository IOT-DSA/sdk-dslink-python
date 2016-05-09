from dslink.JsonSerializer import JsonEncoder
from dslink.Request import Request
from dslink.Response import Response

import json
import logging

from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
from autobahn.websocket.protocol import parseWsUrl
from twisted.internet import reactor, task
from twisted.internet.protocol import ReconnectingClientFactory


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
        self.connector = reactor.connectTCP(url.hostname, port, factory)


class DSAWebSocketFactory(WebSocketClientFactory, ReconnectingClientFactory):
    def __init__(self, websocket_uri, link):
        super(DSAWebSocketFactory, self).__init__(websocket_uri)
        self.link = link
        self.cooldown = 1
    
    def clientConnectionFailed(self, connector, reason):
        self.link.logger.info("Failed to connect")
        reactor.callLater(1, self.reconnect, connector)

    def clientConnectionLost(self, connector, unused_reason):
        self.link.logger.info("Connection lost")
        reactor.callLater(1, self.reconnect, connector)

    def reconnect(self, connector):
        if not self.link.handshake.run_handshake():
            if self.cooldown <= 60:
                self.cooldown += 1
            reactor.callLater(self.cooldown, self.reconnect, connector)
            return
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
        if self.link.active:
            self.logger.debug("Ping")
            # noinspection PyTypeChecker
            self.sendMessage({})

    def onOpen(self):
        """
        WebSocket open event.
        """
        self.link.active = True
        self.logger.info("WebSocket Connection Established")
        task.LoopingCall(self.sendPingMsg).start(self.link.config.ping_time)

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
            if "msg" in i:
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
                    if isinstance(update, list):
                        sid = update[0]
                        val = update[1]
                        time = update[2]
                        self.link.requester.subscription_manager.run_callback(sid, val, time)
                    elif isinstance(update, dict):
                        def get_value(vlist, key, default):
                            if key in vlist:
                                return vlist[key]
                            return default
                        sid = update["sid"]
                        val = update["value"]
                        time = update["ts"]
                        count = get_value(update, "count", 0)
                        sum = get_value(update, "sum", 0)
                        min = get_value(update, "min", 0)
                        max = get_value(update, "max", 0)
                        self.link.requester.subscription_manager.run_callback(sid, val, time, count, sum, min, max)
            elif response["rid"] in self.link.requester.request_manager.requests:
                self.link.requester.request_manager.invoke_request(response["rid"], response)

    def sendMessage(self, payload, isBinary=False, fragmentSize=None, sync=False, doNotCompress=False):
        """
        Send a message over the WebSocket.
        :param payload: Message to send.
        """
        payload["msg"] = self.msg
        self.msg += 1
        payload = json.dumps(payload, sort_keys=True, cls=JsonEncoder)
        self.logger.debug("Sent data: %s" % payload)
        payload = payload.encode("utf-8")
        super(DSAWebSocket, self).sendMessage(payload, isBinary, fragmentSize, sync, doNotCompress)
