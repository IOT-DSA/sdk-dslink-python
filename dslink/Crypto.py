import base64
import hashlib
import os.path
import pickle
#import pyelliptic
from rubenesque.codecs.sec import encode, decode
import rubenesque.curves


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
        pubkey = self.keypair.generator() * self.keypair.private_key()
        sha = hashlib.sha256(encode(pubkey))
        self.b64 = base64.urlsafe_b64encode(sha.digest()).decode("utf-8").replace("=", "")
        self.encoded_public = base64.urlsafe_b64encode(encode(pubkey)).decode("utf-8").replace("=", "")

    def generate_key(self):
        """
        Generate a key.
        """
        self.keypair = rubenesque.curves.find("secp256r1")

    def load_keys(self):
        """
        Load the keys from a file.
        """
        file = open(self.location, "rb")
        try:
            keys = pickle.load(file)
        except ValueError:
            raise ValueError("Could not load serialized keys. Possibly a Python version mismatch. "
                             "Try deleting your .keys file and try running again.")
        #self.keypair = pyelliptic.ECC(curve="prime256v1",
                                      #pubkey_x=keys["pubkey_x"],
                                      #pubkey_y=keys["pubkey_y"],
                                      #raw_privkey=keys["privkey"])
        self.keypair = rubenesque.curves.find("secp256r1")
        self.keypair.create(keys["pubkey_x"], keys["pubkey_y"])

    def save_keys(self):
        """
        Save the keys to a file.
        """
        file = open(self.location, "wb")
        pickle.dump({
            "pubkey_x": self.keypair.generator().x,
            "pubkey_y": self.keypair.generator().y
        }, file)
        file.close()
