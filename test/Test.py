from threading import Timer

from dslink.DSLink import DSLink, Configuration, Node

link = DSLink(Configuration("python-test", "http://localhost:8080/conn", responder=True, requester=True))

def updateFakeValue():
    link.super_root.get("/TestValue").set_value(link.super_root.get("/TestValue").value + 1)
    i = Timer(1, updateFakeValue, ())
    i.start()

testValue = Node("TestValue", link.super_root)
link.super_root.add_child(testValue)
testValue.set_value(1)
testValue.config["$type"] = "number"
updateFakeValue()
