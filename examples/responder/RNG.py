import random

from dslink.DSLink import DSLink, Configuration
from dslink.Node import Node
from twisted.internet import reactor


class RNGDSLink(DSLink):
    def start(self):
        self.speed = 1
        self.rngs = {}

        self.responder.profile_manager.create_profile("rng")

        self.responder.profile_manager.create_profile("create_rng")
        self.responder.profile_manager.register_callback("create_rng", self.create_rng)

        self.responder.profile_manager.create_profile("set_speed")
        self.responder.profile_manager.register_callback("set_speed", self.set_speed)

        self.responder.profile_manager.create_profile("delete_rng")
        self.responder.profile_manager.register_callback("delete_rng", self.delete_rng)

        self.restore_rngs()
        self.update_rng()

    def get_default_nodes(self, super_root):
        create_rng = Node("create_rng", super_root)
        create_rng.set_display_name("Create RNG")
        create_rng.set_config("$is", "create_rng")
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

        set_speed = Node("set_speed", super_root)
        set_speed.set_display_name("Set Speed")
        set_speed.set_config("$is", "set_speed")
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

        temp = Node("temp", super_root)
        temp.set_invokable("config")

        super_root.add_child(create_rng)
        super_root.add_child(set_speed)
        super_root.add_child(temp)

        return super_root

    def create_rng(self, data):
        name = data[1]["Name"]
        if self.responder.get_super_root().get("/%s" % name) is None:
            rng = Node(name, self.responder.get_super_root())
            rng.set_config("$is", "rng")
            rng.set_type("number")
            rng.set_value(0)
            self.responder.get_super_root().add_child(rng)
            delete = Node("delete", rng)
            delete.set_config("$is", "delete_rng")
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

    def set_speed(self, data):
        self.speed = data[1]["Speed"]
        return [
            [
                True
            ]
        ]

    def delete_rng(self, data):
        del self.rngs[data[0].parent.name]
        self.responder.get_super_root().remove_child(data[0].parent.name)
        return [[]]

    def restore_rngs(self):
        for child in self.responder.get_super_root().children:
            node = self.responder.get_super_root().children[child]
            if node.get_config("$is") == "rng":
                self.rngs[node.name] = node

    def update_rng(self):
        for rng in self.rngs:
            if self.rngs[rng].is_subscribed():
                self.rngs[rng].set_value(random.randint(0, 1000))
        reactor.callLater(self.speed, self.update_rng)

if __name__ == "__main__":
    RNGDSLink(Configuration("python-rng", responder=True, requester=True))
