import json
import msgpack

from dslink.Util import base64_encode


class Serializer:
    def is_binary(self):
        """
        Determines whether we are using binary, and need to send like that.
        :return: True if binary, false if text based.
        """
        raise NotImplementedError()

    def load(self, data):
        """
        Deserialize incoming data.
        :param data: Data in serialized form
        :return: Python object containing incoming data
        """
        raise NotImplementedError()

    def dump(self, data):
        """
        Serialize outgoing data.
        :param data: Python object containing outgoing data
        :return: Data in serialized form
        """
        raise NotImplementedError()


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) == bytearray or type(obj) == bytes:
            import base64
            return "\x1Bbytes:" + base64.urlsafe_b64encode(obj).decode("utf-8")
        else:
            return json.JSONEncoder.default(self, obj)


class JsonSerializer(Serializer):
    def is_binary(self):
        return False

    def load(self, data):
        return json.loads(data)

    def dump(self, data):
        return json.dumps(data, sort_keys=True, cls=JsonEncoder)


def msgpack_encode(obj):
    if isinstance(obj, bytearray):
        # TODO
        return "\x1Bbytes:" + base64_encode(obj)
    return obj


class MsgPackSerializer(Serializer):
    def is_binary(self):
        return True

    def load(self, data):
        return msgpack.unpackb(data)

    def dump(self, data):
        return msgpack.packb(data, default=msgpack_encode)


serializers = {
    "json": JsonSerializer(),
    #"msgpack": MsgPackSerializer()
}
