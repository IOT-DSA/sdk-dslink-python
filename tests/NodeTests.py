import unittest

from dslink.Node import Node

class NodeValueTests(unittest.TestCase):
    def test(self):
        floatnode = Node(None, None)
        floatnode.set_type("number")
        floatnode.set_invokable("config")
        floatnode.set_value(0.0)
        self.assertEqual(floatnode.get_type(), "number")
        self.assertEqual(floatnode.get_value(), 0.0)
        self.assertEqual(floatnode.get_config("$invokable"), "config")

        intnode = Node(None, None)
        intnode.set_type("int")
        intnode.set_value(1)
        self.assertEqual(intnode.get_type(), "int")
        self.assertEqual(intnode.get_value(), 1)

        enumnode = Node(None, None)
        enumnode.set_type("enum")
        enumnode.set_value(["test", "hi"])
        self.assertEqual(enumnode.get_type(), "enum")
        self.assertEqual(enumnode.get_value(), "enum[test,hi]")
