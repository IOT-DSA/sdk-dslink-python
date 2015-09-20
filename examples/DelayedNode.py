import random
from time import sleep
from threading import Timer

from dslink.DSLink import DSLink, Configuration, Node


class DelayedNodeDSLink(DSLink):
    def __init__(self):
        super().__init__(Configuration("python-delay", "http://localhost:8080/conn", responder=True, requester=True))
        self.testValue = Node("TestValue", self.super_root)
        self.super_root.add_child(self.testValue)
        self.testValue.set_type("number")
        self.testValue.set_value(1)
        self.updateRandomValue()
        sleep(5)
        self.super_root.add_child(Node("DelayedNode", self.super_root))

    def updateRandomValue(self):
        self.testValue.set_value(random.randint(0, 1000))
        i = Timer(1, self.updateRandomValue, ())
        i.start()

if __name__ == "__main__":
    DelayedNodeDSLink()
