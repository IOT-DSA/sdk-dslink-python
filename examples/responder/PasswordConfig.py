from dslink.DSLink import DSLink, Configuration


class PasswordConfigDSLink(DSLink):
    def get_default_nodes(self, super_root):
        test = super_root.create_child("Test")
        test.set_config("$$password", "Test123")

        return super_root

if __name__ == "__main__":
    PasswordConfigDSLink(Configuration("python-passwordconfig", responder=True, no_save_nodes=True))
