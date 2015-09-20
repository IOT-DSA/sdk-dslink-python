from threading import Timer
import random

from dslink.DSLink import DSLink, Configuration, Node

link = DSLink(Configuration("python-rng", "http://localhost:8080/conn", responder=True, requester=True))

def updateRandomValue():
    link.super_root.get("/TestValue").set_value(random.randint(0, 1000))
    i = Timer(1, updateRandomValue, ())
    i.start()

testValue = Node("TestValue", link.super_root)
link.super_root.add_child(testValue)
testValue.set_type("number")
testValue.set_value(1)
updateRandomValue()
