from __future__ import print_function
from dslink.Profile import ProfileManager
from dslink.Node import Node

import json
import os.path
from twisted.internet import task


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
            task.LoopingCall(self.save_nodes).start(5)

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
            except Exception as e:
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


# TODO: maybe rename to something more fitting?
class Subscription:
    def __init__(self, path, sid_qos):
        self.path = path
        self.sid_qos = sid_qos


class LocalSubscriptionManager:
    """
    Manages subscriptions to local Nodes.
    """

    def __init__(self, link):
        self.link = link
        self.path_subs = {}
        self.sids_path = {}
        subs = self.link.storage.read()
        for path in subs:
            sub = subs[path]
            self.path_subs[path] = Subscription(path, {-1: sub["qos"]})

    def get_sub(self, path):
        path = Node.normalize_path(path, True)
        if path not in self.path_subs:
            return None
        return self.path_subs[path]

    def add_value_sub(self, node, sid, qos=0):
        """
        Store a Subscription to a Node.
        :param node: Node to subscribe to.
        :param sid: SID of Subscription.
        :param qos: Quality of Service.
        """
        path = Node.normalize_path(node.path, True)

        if path not in self.path_subs:
            sub = Subscription(path, {sid: qos})
            self.path_subs[path] = sub
        else:
            self.path_subs[path].sid_qos[sid] = qos
            self.path_subs[path].qos = qos
        self.sids_path[sid] = path
        updates = self.link.storage.get_updates(path, sid)
        if updates is not None:
            self.link.wsp.sendMessage({
                "responses": [
                    {
                        "rid": 0,
                        "updates": updates
                    }
                ]
            })
        else:
            node.update_subscribers_values()

    def remove_value_sub(self, sid):
        """
        Remove a Subscription to a Node.
        :param sid: SID of Subscription.
        """
        if sid in self.sids_path:
            path = self.sids_path[sid]
            del self.sids_path[sid]
            if path in self.path_subs:
                del self.path_subs[path].sid_qos[sid]

    def send_value_update(self, node):
        if node.path not in self.path_subs:
            return
        msg = {
            "responses": []
        }
        for sid in self.path_subs[node.path].sid_qos:
            qos = self.path_subs[node.path].sid_qos[sid]
            if not self.link.active and qos > 0:
                self.link.storage.store(self.path_subs[node.path], node.value)
            msg["responses"].append({
                "rid": 0,
                "updates": [
                    [
                        sid,
                        node.value.value,
                        node.value.updated_at.isoformat()
                    ]
                ]
            })
        if len(msg["responses"]) is not 0:
            self.link.wsp.sendMessage(msg)


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
