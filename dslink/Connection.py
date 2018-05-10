import asyncio
import logging

from .Handshake import Handshake
from .Serializers import JsonSerializer
from .WebSocket import WebSocket


class Connection:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.delay = 0
        self.serializer = JsonSerializer()
        self.handshake = Handshake(self.config)
        self.websocket = WebSocket(self.on_message, self.on_close)
        self.ping_task = None
        self.on_message_callback = None

    async def connect(self):
        while True:
            # Increment delay timer, in case of failure.
            if self.delay < 60:
                self.delay += 1
            try:
                hs_res = self.handshake.run_handshake()
                if hs_res:
                    ws_res = await self.websocket.connect(self.config.get_ws_uri())
                    if ws_res:
                        self.ping_task = asyncio.get_event_loop().create_task(self.ping())
                        break
            except Exception as e:
                self.logger.error("Exception during connect: %s" % str(e))
            self.logger.warning("Failed to connect, attempting reconnect in %i seconds" % self.delay)
            await asyncio.sleep(self.delay)
        self.logger.info("Connected")
        self.delay = 0

    def send(self, msg):
        data = self.serializer.dump(msg)
        self.logger.debug("Sent: %s", data)
        return self.websocket.send(data)

    @asyncio.coroutine
    async def on_message(self, msg):
        self.logger.debug("Recv: %s", msg)
        data = self.serializer.load(msg)
        if self.on_message_callback is not None:
            await self.on_message_callback(data)

    async def on_close(self):
        self.logger.info("Disconnected")
        self.ping_task.cancel()
        await self.connect()

    @asyncio.coroutine
    async def ping(self):
        while True:
            self.logger.debug("Sent ping")
            await self.websocket.send("{}")
            await asyncio.sleep(30)
