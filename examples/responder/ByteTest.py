import dslink


class ByteTest(dslink.DSLink):
    def get_default_nodes(self, super_root):
        test = super_root.create_child("test")
        test.set_type("binary")
        test.set_value(bytes([1, 2, 3, 4, 5]))


if __name__ == "__main__":
    ByteTest(dslink.Configuration("python-bytetest", responder=True, no_save_nodes=True))
