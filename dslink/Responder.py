from dslink.Profile import ProfileManager


class Responder:
    def __init__(self, link):
        self.link = link
        self.subscription_manager = LocalSubscriptionManager(link)
        self.stream_manager = StreamManager(link)
        self.profile_manager = ProfileManager(link)


class LocalSubscriptionManager:
    """
    Manages subscriptions to local Nodes.
    """

    def __init__(self, link):
        self.link = link
        self.subscriptions = {}

    def subscribe(self, node, sid):
        """
        Store a Subscription to a Node.
        :param node: Node to subscribe to.
        :param sid: SID of Subscription.
        """
        self.subscriptions[sid] = node
        self.subscriptions[sid].add_subscriber(sid)

    def unsubscribe(self, sid):
        """
        Remove a Subscription to a Node.
        :param sid: SID of Subscription.
        """
        try:
            self.subscriptions[sid].remove_subscriber(sid)
            del self.subscriptions[sid]
        except KeyError:
            self.link.logger.debug("Unknown sid %s" % sid)


class StreamManager:
    """
    Manages streams for Nodes.
    """

    def __init__(self, link):
        """
        Constructor of StreamManager.
        """
        self.link = link
        self.streams = {}

    def open_stream(self, node, rid):
        """
        Open a Stream.
        :param node: Node to handle streaming.
        :param rid: RID of Stream.
        """
        self.streams[rid] = node
        self.streams[rid].streams.append(rid)

    def close_stream(self, rid):
        """
        Close a Stream.
        :param rid: RID of Stream.
        """
        try:
            self.streams[rid].streams.remove(rid)
            del self.streams[rid]
        except KeyError:
            self.link.logger.debug("Unknown rid %s" % rid)


