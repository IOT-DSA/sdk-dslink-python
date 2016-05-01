from dslink.Util import *
from dslink.Value import Value
from dslink.storage.Storage import StorageDriver

import json
import os
import pickle


class FileStorage(StorageDriver):
    def __init__(self, link, path="storage/"):
        StorageDriver.__init__(self)
        self.link = link
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
            file = open(self.storage + "/" + f, "rb")
            json_obj = pickle.load(file)
            file.close()
            qos = json_obj["qos"]
            path = base64_decode(f)
            sub = {
                "path": path,
                "qos": qos
            }
            ret[path] = sub
            if qos is 2:
                value = Value()
                value.type = json_obj["type"]
                value.updated_at = json_obj["ts"]
                value.value = json_obj["value"]
                self.store(sub, value)
                self.update_cache[path] = value
            elif qos is 3:
                try:
                    import_queue = json_obj["queue"]
                except KeyError:
                    continue

                if path not in self.updates_cache or sub["path"] not in self.updates_cache:
                    queue = []
                elif path in self.updates_cache:
                    queue = self.updates_cache[path]
                elif sub["path"] in self.updates_cache:
                    queue = self.updates_cache[sub["path"]]
                else:
                    continue

                for array in import_queue:
                    value = Value()
                    value.type = array[0]
                    value.updated_at = array[1]
                    value.value = array[2]
                    queue.append(value)
        return ret

    def store(self, subscription, value):
        qos = subscription.qos
        json_obj = None
        if qos is 2:
            self.update_cache[subscription.path] = value
            json_obj = {
                "qos": 2
            }
            if value is not None:
                json_obj["type"] = value.type
                json_obj["ts"] = value.updated_at
                json_obj["value"] = value.value
        elif qos is 3:
            if value is None:
                return
            if subscription.path in self.updates_cache:
                cache = self.updates_cache[subscription.path]
            else:
                cache = []
                self.updates_cache[subscription.path] = cache
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
                        v.type,
                        v.updated_at,
                        v.value
                    ]
                    queue.append(array)
        if json_obj is not None:
            if not(os.path.exists(self.storage) or os.mkdir(self.storage)):
                pass
            file = open(self.storage + base64_encode(subscription.path), "wb")
            pickle.dump(json_obj, file)
            file.close()

    def get_updates(self, path, sid):
        cache = self.updates_cache.pop(path, None)
        tmp = self.updates_cache.pop(path, None)
        if tmp is not None:
            return [
                sid,
                tmp.value.value,
                tmp.value.updated_at.isoformat()
            ]
        if cache is None or len(cache) is 0:
            return None
        updates = []
        for val in cache:
            update = [
                sid,
                val.value,
                val.updated_at.isoformat()
            ]
            updates.append(update)
            file_path = self.storage + base64_encode(path)
            if os.path.exists(file_path):
                os.remove(file_path)
        return updates
