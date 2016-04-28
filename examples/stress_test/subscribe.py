import dslink


class SubscribeDSLink(dslink.DSLink):
    def __init__(self, config):
        self.i = 0
        dslink.DSLink.__init__(self, config)

    def start(self):
        self.requester.subscribe("/data/test", self.value_update)

    def value_update(self, data):
        got = int(data[0][-6:])
        if got != self.i:
            #print(data[3])
            print("%s != %s" % (got, self.i))
            print("%s %s %s" % (data[3], data[4], data[5]))
            self.i = got + 1
        else:
            self.i += 1

if __name__ == "__main__":
    SubscribeDSLink(dslink.Configuration("subscribe", requester=True, responder=True))

