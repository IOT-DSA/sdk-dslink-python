import dslink


class ByteTest(dslink.DSLink):
    def start(self):
        self.requester.set("/downstream/python-bytetest/test", bytearray([0x00, 0x01]))

if __name__ == "__main__":
    ByteTest(dslink.Configuration("python-bytetestrequester", requester=True))
