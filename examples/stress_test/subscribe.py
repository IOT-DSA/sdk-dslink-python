import dslink
from twisted.internet import reactor

class SubscribeDSLink(dslink.DSLink):
    i=0
    def start(self):
        self.requester.subscribe("/data/test", self.value_update)
        #reactor.callLater(5, self.unsubscribe)

    def value_update(self, data):
        #print "Data: ", data[0]
        SubscribeDSLink.i = SubscribeDSLink.i+1
        print "Count: ", (SubscribeDSLink.i)

if __name__ == "__main__":
    SubscribeDSLink(dslink.Configuration("subscribe", requester=True, responder=True))

