import dslink


class RngDSLink(dslink.DSLink):
    def __init__(self):
        super().__init__()
        self.name = "python-rng"
        self.is_responder = True

    def on_connected(self):
        print("Connected")

    def on_disconnected(self):
        print("Disconnected")


if __name__ == "__main__":
    import logging
    import sys
    logging.getLogger("dslink").addHandler(logging.StreamHandler(sys.stdout))
    logging.getLogger("dslink").setLevel(logging.DEBUG)
    dslink.dslink_run(
        RngDSLink(),
        [
            "--broker=http://localhost:8090/conn",
            "--log=debug"
        ]
    )
