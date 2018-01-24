import base64
import hashlib
import os.path
import pickle
from rubenesque.codecs.sec import encode, decode
from rubenesque.curves import find
from rubenesque.curves.sec import secp256r1


curve = find("secp256r1")


class Crypto:
    """
    Class to handle keypair generation, loading, and saving.
    """

    def __init__(self, location):
        """
        Keypair Constructor.
        """
        self.location = location
        if not os.path.isfile(self.location):
            self.keypair = KeyPair(KeyPair.generate_private_key())
            self.save_keys()
        else:
            self.load_keys()
        sha = hashlib.sha256(encode(self.keypair.get_public_key(), False))
        self.b64 = base64.urlsafe_b64encode(sha.digest()).decode("utf-8").replace("=", "")
        self.encoded_public = base64.urlsafe_b64encode(encode(self.keypair.get_public_key(), False)).decode("utf-8").replace("=", "")

    def load_keys(self):
        """
        Load the keys from a file.
        """
        file = open(self.location, "rb")
        try:
            keys = pickle.load(file)
        except ValueError:
            raise ValueError("Could not load serialized key. Possibly a Python version mismatch. "
                             "Try deleting your .keys file and try running again.")
        self.keypair = KeyPair(keys["private"])

    def save_keys(self):
        """
        Save the keys to a file.
        """
        file = open(self.location, "wb")
        pickle.dump({
            "private": self.keypair.private_key
        }, file)
        file.close()

    @staticmethod
    def encode_shared_secret(point):
        return encode(point, False)


class KeyPair:
    def __init__(self, private_key):
        self.private_key = private_key

    def get_public_key(self):
        return curve.generator() * self.private_key

    def generate_shared_secret(self, public_key):
        return public_key * self.private_key

    @staticmethod
    def generate_private_key():
        return curve.private_key()

    @staticmethod
    def decode_tempkey(bytes):
        return decode(secp256r1, bytes)
