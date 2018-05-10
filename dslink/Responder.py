import logging

from .Node import Node


class Responder:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.super_root = Node(None, None)

    async def parse(self, requests):
        responses = []
        for request in requests:
            method = request["method"]
            if method == "list":
                response = await self.list(request)
            elif method == "set":
                response = await self.set(request)
            elif method == "remove":
                response = await self.remove(request)
            elif method == "invoke":
                response = await self.invoke(request)
            elif method == "subscribe":
                response = await self.subscribe(request)
            elif method == "unsubscribe":
                response = await self.unsubscribe(request)
            elif method == "close":
                response = await self.close(request)
            else:
                raise NotImplementedError("Unimplemented or unknown request method: %s", request["method"])
            if response is not None:
                responses.append(response)
        return responses

    async def list(self, request):
        rid = request["rid"]
        path = request["path"]
        return {
            "rid": rid,
            "stream": "open",
            "updates": self.super_root.get(path).stream()
        }

    async def set(self, request):
        pass

    async def remove(self, request):
        pass

    async def invoke(self, request):
        pass

    async def subscribe(self, request):
        pass

    async def unsubscribe(self, request):
        pass

    async def close(self, request):
        pass
