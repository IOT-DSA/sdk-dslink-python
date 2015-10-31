import random

from dslink.DSLink import DSLink, Configuration, Node
from dslink.Profile import Profile
from twisted.internet import reactor


class RNGDSLink(DSLink):
    def __init__(self):
        DSLink.__init__(self, Configuration("python-rng", responder=True, requester=True))
        self.speed = 1
        self.rngs = {}

        self.profile_manager.create_profile(Profile("rng"))

        self.profile_manager.create_profile(Profile("createRNG"))
        self.profile_manager.register_callback("createRNG", self.create_rng)

        self.profile_manager.create_profile(Profile("setSpeed"))
        self.profile_manager.register_callback("setSpeed", self.set_speed)

        self.profile_manager.create_profile(Profile("deleteRNG"))
        self.profile_manager.register_callback("deleteRNG", self.delete_rng)

        self.restore_rngs()
        self.update_rng()

    def get_default_nodes(self):
        root = self.get_root_node()

        create_rng = Node("createRNG", root)
        create_rng.set_config("$name", "Create RNG")
        create_rng.set_config("$is", "createRNG")
        create_rng.set_invokable("config")
        create_rng.set_parameters([
            {
                "name": "Name",
                "type": "string"
            }
        ])
        create_rng.set_columns([
            {
                "name": "Success",
                "type": "bool"
            }
        ])
        root.add_child(create_rng)
        set_speed = Node("setSpeed", root)
        set_speed.set_config("$name", "Set Speed")
        set_speed.set_config("$is", "setSpeed")
        set_speed.set_invokable("config")
        set_speed.set_parameters([
            {
                "name": "Speed",
                "type": "number"
            }
        ])
        set_speed.set_columns([
            {
                "name": "Success",
                "type": "bool"
            }
        ])
        root.add_child(set_speed)
        return root

    def create_rng(self, obj):
        name = obj.params["Name"]
        if self.super_root.get("/%s" % name) is None:
            rng = Node(name, self.super_root)
            rng.set_config("$is", "rng")
            rng.set_type("number")
            rng.set_value(0)
            self.super_root.add_child(rng)
            delete = Node("delete", rng)
            delete.set_config("$is", "deleteRNG")
            delete.set_invokable("config")
            rng.add_child(delete)
            self.rngs[name] = rng
            return [
                [
                    True
                ]
            ]
        return [
            [
                False
            ]
        ]

    def set_speed(self, obj):
        self.speed = obj.params["Speed"]
        return [
            [
                True
            ]
        ]

    def delete_rng(self, obj):
        del self.rngs[obj.node.parent.name]
        self.super_root.remove_child(obj.node.parent.name)
        return [
            []
        ]

    def restore_rngs(self):
        for child in self.super_root.children:
            node = self.super_root.children[child]
            if node.get_config("$is") == "rng":
                self.rngs[node.name] = node
                print(self.rngs)
                node.set_value(1)

    def update_rng(self):
        for rng in self.rngs:
            if self.rngs[rng].is_subscribed():
                self.rngs[rng].set_value(random.randint(0, 1000))
        reactor.callLater(self.speed, self.update_rng)

if __name__ == "__main__":
    RNGDSLink()
