import asyncio
import websockets


class WebSocket:
    def __init__(self, on_msg, on_close):
        self.on_msg = on_msg
        self.on_close = on_close
        self.client = None

    @property
    def is_connected(self):
        return self.client is not None

    async def connect(self, uri):
        self.client = await websockets.connect(uri)
        asyncio.get_event_loop().create_task(self.message_listener())
        return True

    def reset(self):
        self.client = None

    @asyncio.coroutine
    async def send(self, msg):
        return self.client.send(msg)

    @asyncio.coroutine
    async def message_listener(self):
        while True:
            try:
                msg = await self.client.recv()
                await self.on_msg(msg)
            except websockets.exceptions.ConnectionClosed:
                await self.on_close()
