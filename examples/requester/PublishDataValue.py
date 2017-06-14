from threading import Thread
import dslink


class PublishDSLink(dslink.DSLink):
    def start(self):
        self.thread = Thread(target=self.thread_function)

    def on_connected(self):
        self.thread.start()

    def on_disconnected(self):
        self.thread.join()

    def thread_function(self):
        i = 0
        while True:
            self.requester.invoke("/data/publish", dslink.Permission.WRITE, params={
                "Path": "/data/test",
                "Value": i,
                "CloseStream": True
            })
            i += 1


if __name__ == "__main__":
    PublishDSLink(dslink.Configuration(name="python-datapublish", requester=True))
