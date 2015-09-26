import unittest

from dslink.Node import Node

class NodeValueTests(unittest.TestCase):
    def test(self):
        node = Node(None, None)
        node.set_type("number")
        node.set_value(0.0)
        self.assertEqual(node.get_type(), "number")
        self.assertEqual(node.get_value(), 0.0)
