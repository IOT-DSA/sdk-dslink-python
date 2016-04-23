from dslink.Util import *

import json


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytearray):
            return "\x1Bbytes:" + base64_encode(obj)
        else:
            return json.JSONEncoder.default(self, obj)
