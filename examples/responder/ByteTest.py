import dslink


class ByteTest(dslink.DSLink):
    def start(self):
        test = self.responder.get_super_root().create_child("test")
        test.set_type("binary")
        test.set_writable(dslink.Permission.WRITE)
        test.set_value(bytearray([0x00, 0x01, 0x02, 0x03, 0x04, 0x05]))

if __name__ == "__main__":
    ByteTest(dslink.Configuration("python-bytetest", responder=True, no_save_nodes=True))
