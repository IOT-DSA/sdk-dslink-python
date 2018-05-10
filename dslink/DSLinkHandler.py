import logging

from .Configuration import Configuration
from .Connection import Connection
from .Responder import Responder


class DSLinkHandler:
    def __init__(self, dslink, options):
        self.logger = logging.getLogger(__name__)
        self.msg = 0
        self.dslink = dslink
        self.config = Configuration(dslink, options)
        self.connection = Connection(self.config)
        self.connection.on_message_callback = self.on_message
        self.responder = Responder()

    async def start(self):
        await self.connection.connect()

    async def on_message(self, msg):
        response = {}
        if "requests" in msg and len(msg["requests"]) > 0:
            response["responses"] = await self.responder.parse(msg["requests"])
        response["msg"] = self.next_msg_id()
        if "msg" in msg:
            response["ack"] = msg["msg"]
        await self.connection.send(response)

    def next_msg_id(self):
        i = self.msg
        self.msg += 1
        return i
