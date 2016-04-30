class StorageDriver:
    def __init__(self):
        pass

    def read(self):
        """
        Read from storage.
        """
        pass

    def store(self, subscription, value):
        """
        Store value in storage.
        """
        pass

    def get_updates(self, path, sid):
        pass
