import json
import msgpack

from dslink.JsonSerializer import JsonEncoder


class Serializer:
    def is_binary(self):
        """
        Determines whether we are using binary, and need to send like that.
        :return: True if binary, false if text based.
        """
        raise NotImplementedError()

    def short_name(self):
        """
        A short name that is passed to the broker during handshake
        to specify what format we are using.
        :return: Short name, e.g. "json", "msgpack"
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


class JsonSerializer(Serializer):
    def is_binary(self):
        return False

    def short_name(self):
        return "json"

    def load(self, data):
        return json.loads(data)

    def dump(self, data):
        return json.dumps(data, sort_keys=True, cls=JsonEncoder)


class MsgPackSerializer(Serializer):
    def is_binary(self):
        return True

    def short_name(self):
        return "msgpack"

    def load(self, data):
        return msgpack.unpackb(data)

    def dump(self, data):
        return msgpack.packb(data, use_bin_type=True)
