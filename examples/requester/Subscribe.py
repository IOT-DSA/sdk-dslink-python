import dslink
from twisted.internet import reactor


class SubscribeDSLink(dslink.DSLink):
    def start(self):
        self.requester.subscribe("/sys/dataOutPerSecond", self.value_update)
        reactor.callLater(5, self.unsubscribe)

    def value_update(self, data):
        print(data[0])

    def unsubscribe(self):
        self.requester.unsubscribe("/sys/dataOutPerSecond")

if __name__ == "__main__":
    SubscribeDSLink(dslink.Configuration(name="SubscribeExample", requester=True))
