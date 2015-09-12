class Response:
    def __init__(self, json):
        self.json = json

    def get_stream(self):
        return self.json
