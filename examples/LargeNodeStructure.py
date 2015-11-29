from dslink.DSLink import DSLink, Configuration, Node


class LargeNodeStructure(DSLink):
    def start(self):
        for x in range(0, 999):
            first = Node("Test%i" % x, self.super_root)
            for y in range(0, 10):
                second = Node("Test%i" % y, first)
                second.set_type("number")
                second.set_value(y)

if __name__ == "__main__":
    LargeNodeStructure(Configuration("python-large", responder=True, requester=True, no_save_nodes=True))
