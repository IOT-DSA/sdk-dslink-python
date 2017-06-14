import unittest

from dslink import Node
from dslink.Serializers import JsonSerializer, MsgPackSerializer
from dslink.Value import ValueType


class SerializerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.json = JsonSerializer()
        cls.msgpack = MsgPackSerializer()
        cls.array = [1, 2, 3, 4, 5]

        simple_node = Node("simple_node", None, standalone=True)
        cls.simple_node = simple_node.to_json()

        adv_node = Node("adv_node", None, standalone=True)
        binary_node = adv_node.create_child("binary_node")
        binary_node.set_type(ValueType.binary)
        binary_node.set_value([0x01, 0x02, 0x03, 0x04, 0x05])
        string_node = adv_node.create_child("string_node")
        string_node.set_type(ValueType.string)
        string_node.set_value("string!")
        int_node = adv_node.create_child("int_node")
        int_node.set_type(ValueType.int)
        int_node.set_value(12345)
        dyn_node = adv_node.create_child("dyn_node")
        dyn_node.set_type(ValueType.dynamic)
        dyn_node.set_value(12345)
        cls.adv_node = adv_node.to_json()

    def testJson(self):
        self.sharedAssertEqual(self.array, self.json)
        self.sharedAssertEqual(self.simple_node, self.json)
        self.sharedAssertEqual(self.adv_node, self.json)

    def testMsgPack(self):
        self.sharedAssertEqual(self.array, self.msgpack)
        self.sharedAssertEqual(self.simple_node, self.msgpack)
        self.sharedAssertEqual(self.adv_node, self.msgpack)

    def sharedAssertEqual(self, data, serializer):
        i = serializer.dump(data)
        i = serializer.load(i)
        self.assertEqual(data, i)
