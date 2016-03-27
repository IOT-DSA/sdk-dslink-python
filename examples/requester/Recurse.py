import dslink


class RecurseDSLink(dslink.DSLink):
    def start(self):
        self.requester.list("/", self.recurse)

    def recurse(self, listresponse):
        for child_name in listresponse.node.children:
            child = listresponse.node.children[child_name]
            print(child.path)
            self.requester.list(child.path, self.recurse)

if __name__ == "__main__":
    RecurseDSLink(dslink.Configuration(name="RecurseExample", requester=True))
