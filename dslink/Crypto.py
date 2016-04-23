import base64
import hashlib
import os.path
import pickle
import pyelliptic


class Keypair:
    """
    Class to handle keypair generation, loading, and saving.
    """

    def __init__(self, location):
        """
        Keypair Constructor.
        """
        self.location = location
        self.keypair = None
        if not os.path.isfile(self.location):
            self.generate_key()
            self.save_keys()
        else:
            self.load_keys()
        sha = hashlib.sha256(self.keypair.get_pubkey())
        self.b64 = base64.urlsafe_b64encode(sha.digest()).decode("utf-8").replace("=", "")
        self.encoded_public = base64.urlsafe_b64encode(self.keypair.get_pubkey()).decode("utf-8").replace("=", "")

    def generate_key(self):
        """
        Generate a key.
        """
        self.keypair = pyelliptic.ECC(curve="prime256v1")

    def load_keys(self):
        """
        Load the keys from a file.
        """
        file = open(self.location, "rb")
        keys = pickle.load(file)
        self.keypair = pyelliptic.ECC(curve="prime256v1",
                                      pubkey_x=keys["pubkey_x"],
                                      pubkey_y=keys["pubkey_y"],
                                      raw_privkey=keys["privkey"])
        file.close()

    def save_keys(self):
        """
        Save the keys to a file.
        """
        file = open(self.location, "wb")
        pickle.dump({
            "pubkey_x": self.keypair.pubkey_x,
            "pubkey_y": self.keypair.pubkey_y,
            "privkey": self.keypair.privkey
        }, file)
        file.close()
