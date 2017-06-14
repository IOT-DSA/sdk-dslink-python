import dslink


class ByteTest(dslink.DSLink):
    def start(self):
        test = self.responder.get_super_root().create_child("test")
        test.set_type("binary")
        test.set_writable(dslink.Permission.WRITE)
        test.set_value(bytearray([1, 2, 3, 4, 5]))

if __name__ == "__main__":
    ByteTest(dslink.Configuration("python-bytetest", responder=True, no_save_nodes=True, comm_format="json"))
