import dslink


class ListDSLink(dslink.DSLink):
    def start(self):
        self.requester.list("/", self.list)

    def list(self, listresponse):
        print(listresponse.node.children)

if __name__ == "__main__":
    ListDSLink(dslink.Configuration(name="ListExample", requester=True))
