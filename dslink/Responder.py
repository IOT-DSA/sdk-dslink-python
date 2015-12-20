import os.path
import json
from twisted.internet import reactor

from dslink.Profile import ProfileManager
from dslink.Node import Node


class Responder:
    def __init__(self, link):
        """
        Create Responder class.
        :param link: DSLink instance.
        """
        self.link = link
        self.nodes_changed = False
        self.subscription_manager = LocalSubscriptionManager(link)
        self.stream_manager = StreamManager(link)
        self.profile_manager = ProfileManager(link)

    def start(self):
        """
        Start Responder.
        :return:
        """
        # Load or create an empty Node structure
        self.super_root = self.load_nodes()
        self.create_defs()

        # Start saving timer
        if not self.link.config.no_save_nodes:
            reactor.callLater(1, self.save_timer)

    def get_super_root(self):
        """
        Get Super Root.
        :return: Super Root.
        """
        return self.super_root

    def create_defs(self):
        """
        Create /defs/ Node.
        """
        defs = Node("defs", self.get_super_root())
        defs.set_transient(True)
        defs.set_config("$hidden", True)
        defs.add_child(Node("profile", defs))
        self.get_super_root().add_child(defs)

    def create_empty_super_root(self):
        """
        Create empty super root.
        :return: Empty Super Root.
        """
        super_root = Node("", None)
        super_root.link = self.link
        return super_root

    # noinspection PyBroadException
    def load_nodes(self):
        """
        Load nodes.json file from disk, use backup if necessary. If that fails, then reset to defaults.
        """
        nodes_path = self.link.config.nodes_path
        if os.path.exists(nodes_path):
            try:
                nodes_file = open(nodes_path, "r")
                obj = json.load(nodes_file)
                nodes_file.close()
                return Node.from_json(obj, None, "", link=self.link)
            except Exception, e:
                print(e)
                self.link.logger.error("Unable to load nodes data")
                if os.path.exists(nodes_path + ".bak"):
                    try:
                        self.link.logger.warn("Restoring backup nodes")
                        os.remove(nodes_path)
                        os.rename(nodes_path + ".bak", nodes_path)
                        nodes_file = open(nodes_path, "r")
                        obj = json.load(nodes_file)
                        nodes_file.close()
                        return Node.from_json(obj, None, "", link=self.link)
                    except:
                        self.link.logger.error("Unable to restore nodes, using default")
                        return self.link.get_default_nodes(self.create_empty_super_root())
                else:
                    self.link.logger.warn("Backup nodes data doesn't exist, using default")
                    return self.link.get_default_nodes(self.create_empty_super_root())
        else:
            return self.link.get_default_nodes(self.create_empty_super_root())

    def save_timer(self):
        """
        Save timer, schedules to call itself every 5 seconds by default.
        """
        self.save_nodes()
        reactor.callLater(5, self.save_timer)

    def save_nodes(self):
        """
        Save the nodes.json out to disk if changed, and create the bak file.
        """
        if self.nodes_changed:
            if os.path.exists(self.link.config.nodes_path + ".bak"):
                os.remove(self.link.config.nodes_path + ".bak")
            if os.path.exists(self.link.config.nodes_path):
                os.rename(self.link.config.nodes_path, self.link.config.nodes_path + ".bak")
            nodes_file = open(self.link.config.nodes_path, "w")
            nodes_file.write(json.dumps(self.get_super_root().to_json(), sort_keys=True, indent=2))
            nodes_file.flush()
            os.fsync(nodes_file.fileno())
            nodes_file.close()
            self.nodes_changed = False


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
