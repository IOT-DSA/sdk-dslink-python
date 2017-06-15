import dslink
import random


class LargeNodeStructure(dslink.DSLink):
    def start(self):
        for x in range(0, 500):
            first = self.responder.get_super_root().create_child("First%i" % x)
            for y in range(0, 200):
                second = first.create_child("Second%i" % y)
                second.set_type(dslink.ValueType.int)
                second.set_value(random.randint(0, 1000000))

if __name__ == "__main__":
    LargeNodeStructure(dslink.Configuration("python-large", responder=True, no_save_nodes=True))
