import dslink


class SubscribeDSLink(dslink.DSLink):
    def __init__(self, config):
        dslink.DSLink.__init__(self, config)
        self.i = 0

    def start(self):
        self.requester.subscribe("/data/test", self.value_update)

    def value_update(self, data):
        self.i += 1
        print("Count: ", self.i)

if __name__ == "__main__":
    SubscribeDSLink(dslink.Configuration("subscribe", requester=True, responder=True))

