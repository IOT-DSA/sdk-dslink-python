import random

from dslink.DSLink import DSLink, Configuration, Node
from dslink.Profile import Profile
from twisted.internet import reactor


class RNGDSLink(DSLink):
    def __init__(self):
        DSLink.__init__(self, Configuration("python-rng", responder=True, requester=True))
        self.speed = 1
        self.rngs = []

        self.profile_manager.create_profile(Profile("createRNG"))
        self.profile_manager.register_callback("createRNG", self.create_rng)

        self.update_rng()

    def get_default_nodes(self):
        root = Node("", None)
        root.link = self
        create_rng = Node("createRNG", root)
        create_rng.set_config("$name", "Create RNG")
        create_rng.set_config("$profile", "createRNG")
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
        if self.super_root.get("/%s" % obj.params["Name"]) is None:
            rng = Node(obj.params["Name"], self.super_root)
            rng.set_type("number")
            rng.set_value(1)
            self.super_root.add_child(rng)
            delete = Node("delete", rng)
            delete.set_invokable("config")
            # TODO delete.set_invoke_callback(self.deleteCallback)
            rng.add_child(delete)
            self.rngs.append(rng)
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

    def setSpeedCallback(self, obj):
        self.speed = obj.params["Speed"]
        return [
            [
                True
            ]
        ]

    def deleteCallback(self, obj):
        # TODO(logangorence): Memory Leak: Remove old RNG.
        self.super_root.remove_child(obj.node.parent.name)
        return [
            []
        ]

    def update_rng(self):
        for rng in self.rngs:
            if rng.is_subscribed():
                rng.set_value(random.randint(0, 1000))
        reactor.callLater(self.speed, self.update_rng)

if __name__ == "__main__":
    RNGDSLink()
