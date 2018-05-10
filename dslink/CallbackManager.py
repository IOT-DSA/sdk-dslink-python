class CallbackManager:
    def __init__(self):
        self.callbacks = []

    def __iadd__(self, new):
        if not callable(new):
            raise Exception("Not a callable function")
        self.callbacks.append(new)
        return self

    def exec(self, *args):
        for call in self.callbacks:
            call(args)
