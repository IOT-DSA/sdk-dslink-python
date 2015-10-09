import random
from threading import Timer

from dslink.DSLink import DSLink, Configuration, Node


class RNGDSLink(DSLink):
    def __init__(self):
        super().__init__(Configuration("python-rng", responder=True, requester=True))
        self.speed = 1
        self.rngs = []
        self.createRNG = Node("createRNG", self.super_root)
        self.createRNG.set_config("$name", "Create RNG")
        self.createRNG.set_invokable("config")
        self.createRNG.set_parameters([
            {
                "name": "Name",
                "type": "string"
            }
        ])
        self.createRNG.set_columns([
            {
                "name": "Success",
                "type": "bool"
            }
        ])
        self.createRNG.set_invoke_callback(self.createCallback)
        self.super_root.add_child(self.createRNG)
        self.setSpeed = Node("setSpeed", self.super_root)
        self.setSpeed.set_config("$name", "Set Speed")
        self.setSpeed.set_invokable("config")
        self.setSpeed.set_parameters([
            {
                "name": "Speed",
                "type": "number"
            }
        ])
        self.setSpeed.set_columns([
            {
                "name": "Success",
                "type": "bool"
            }
        ])
        self.setSpeed.set_invoke_callback(self.setSpeedCallback)
        self.super_root.add_child(self.setSpeed)
        self.update_rng()

    def createCallback(self, params):
        if self.super_root.get("/%s" % params["Name"]) is None:
            rng = Node(params["Name"], self.super_root)
            rng.set_type("number")
            rng.set_value(1)
            self.super_root.add_child(rng)
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

    def setSpeedCallback(self, params):
        self.speed = params["Speed"]
        return [
            [
                True
            ]
        ]

    def update_rng(self):
        for rng in self.rngs:
            if rng.is_subscribed():
                rng.set_value(random.randint(0, 1000))
        i = Timer(self.speed, self.update_rng, ())
        i.start()

if __name__ == "__main__":
    RNGDSLink()
