from dslink.Util import *
from dslink.storage.Storage import StorageDriver

import json
import os


class FileStorage(StorageDriver):
    def __init__(self, path="storage/"):
        StorageDriver.__init__(self)
        self.storage = path
        self.updates_cache = {}
        self.update_cache = {}

    def read(self):
        ret = {}
        if not os.path.isdir(self.storage):
            return
        files = os.listdir(self.storage)
        if len(files) is 0:
            return
        for f in files:
            file = open(self.storage + "/" + f, "r")
            data = file.readline()
            file.close()
            json_obj = json.loads(data)
            qos = json_obj["qos"]
            path = base64_decode(f)
            sub = {
                "path": path,
                "qos": qos
            }
            ret[path] = sub
            if qos is 2:
                ts = json_obj["ts"]

    def store(self, subscription, value):
        qos = subscription["qos"]
        json_obj = None
        if qos is 2:
            self.update_cache[subscription["node"].path] = value
            json_obj = {
                "qos": 2
            }
            if value is not None:
                json_obj["value"] = value.value
                json_obj["ts"] = value.updated_at.isoformat()
        elif qos is 3:
            if value is None:
                return
            if subscription["node"].path in self.updates_cache:
                cache = self.updates_cache[subscription["node"].path]
            else:
                cache = []
                self.updates_cache[subscription["node"].path] = cache
            cache.append(value)
            if len(cache) > 1000:
                del cache[0]
            queue = []
            json_obj = {
                "queue": queue,
                "qos": 3
            }
            for v in cache:
                if value is None:
                    queue.append(None)
                else:
                    array = [
                        v.value,
                        v.updated_at.isoformat()
                    ]
                    queue.append(array)
        if json_obj is not None:
            if not(os.path.exists(self.storage) or os.mkdir(self.storage)):
                pass
            file = open(self.storage + base64_encode(subscription["node"].path), "w")
            file.write(json.dumps(json_obj))
            file.close()

    def get_updates(self, subscription):
        pass
