import dslink


class LargeNodeStructure(dslink.DSLink):
    def start(self):
        for x in range(0, 99):
            first = dslink.Node("First%i" % x, self.responder.get_super_root())
            for y in range(0, 99):
                second = dslink.Node("Second%i" % y, first)
                first.add_child(second)
            self.responder.get_super_root().add_child(first)

if __name__ == "__main__":
    LargeNodeStructure(dslink.Configuration("python-large", responder=True, no_save_nodes=True))
