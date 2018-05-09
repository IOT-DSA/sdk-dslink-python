class DSLink:
    def __init__(self):
        self.name = "python-dslink"
        self.is_responder = False
        self.is_requester = False

    def on_connected(self):
        pass

    def on_disconnected(self):
        pass
