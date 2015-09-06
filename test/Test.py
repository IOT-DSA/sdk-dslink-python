from sdk.DSLink import DSLink, Configuration

link = DSLink(Configuration("python-test", "http://localhost:8080/conn", responder=True))
