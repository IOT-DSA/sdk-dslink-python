class Response:
    def __init__(self, response):
        self.rid = response["rid"]
        self.stream = response["stream"]
        self.updates = response["updates"]

    def stream(self):
        s = {}
        s["rid"] = self.rid
        s["stream"] = self.stream
        s["updates"] = self.updates
        return s
