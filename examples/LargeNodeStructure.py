from dslink.DSLink import DSLink, Configuration, Node


class LargeNodeStructure(DSLink):
    def __init__(self):
        super().__init__(Configuration("python-large", "http://localhost:8080/conn", responder=True, requester=True))
        for x in range(0, 999):
            first = Node("Test%i" % x, self.super_root)
            for y in range(0, 99):
                first.add_child(Node("Test%i" % y, first))
            self.super_root.add_child(first)

if __name__ == "__main__":
    LargeNodeStructure()
