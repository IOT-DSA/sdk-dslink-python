import base64
import unittest

from dslink.Crypto import Keypair
from dslink.Util import base64_add_padding


class CryptoTests(unittest.TestCase):
    clientPrivate = "M6S41GAL0gH0I97Hhy7A2-icf8dHnxXPmYIRwem03HE"
    clientPublic = "BEACGownMzthVjNFT7Ry-RPX395kPSoUqhQ_H_vz0dZzs5RYoVJKA16XZhdYd__ksJP0DOlwQXAvoDjSMWAhkg4"
    clientDsId = "test-s-R9RKdvC2VNkfRwpNDMMpmT_YWVbhPLfbIc-7g4cpc"
    serverTempPrivate = "rL23cF6HxmEoIaR0V2aORlQVq2LLn20FCi4_lNdeRkk"
    serverTempPublic = "BCVrEhPXmozrKAextseekQauwrRz3lz2sj56td9j09Oajar0RoVR5Uo95AVuuws1vVEbDzhOUu7freU0BXD759U"
    sharedSecret = "116128c016cf380933c4b40ffeee8ef5999167f5c3d49298ba2ebfd0502e74e3"
    hashedAuth = "V2P1nwhoENIi7SqkNBuRFcoc8daWd_iWYYDh_0Z01rs"

    def decode(self, data):
        return base64.urlsafe_b64decode(base64_add_padding(data).encode("utf-8"))

    def test(self):
        tempkey = Keypair.decode_tempkey(self.decode(self.serverTempPublic))
