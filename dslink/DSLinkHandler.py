import logging

from .Configuration import Configuration
from .Connection import Connection


class DSLinkHandler:
    def __init__(self, dslink, options):
        self.logger = logging.getLogger(__name__)
        self.dslink = dslink
        self.config = Configuration(dslink, options)
        self.connection = Connection(self.config)

    async def start(self):
        await self.connection.connect()
