import base64
import hashlib
import unittest

from dslink.Crypto import KeyPair
from dslink.Util import base64_add_padding

from dslink.rubenesque.lcodec import ldec, lenc
from dslink.rubenesque.codecs.sec import encode, decode
from dslink.rubenesque.curves.sec import secp256r1


class CryptoTests(unittest.TestCase):
    clientPrivate = "M6S41GAL0gH0I97Hhy7A2-icf8dHnxXPmYIRwem03HE"
    clientPublic = "BEACGownMzthVjNFT7Ry-RPX395kPSoUqhQ_H_vz0dZzs5RYoVJKA16XZhdYd__ksJP0DOlwQXAvoDjSMWAhkg4"
    clientDsId = "test-s-R9RKdvC2VNkfRwpNDMMpmT_YWVbhPLfbIc-7g4cpc"
    serverTempPrivate = "rL23cF6HxmEoIaR0V2aORlQVq2LLn20FCi4_lNdeRkk"
    serverTempPublic = "BCVrEhPXmozrKAextseekQauwrRz3lz2sj56td9j09Oajar0RoVR5Uo95AVuuws1vVEbDzhOUu7freU0BXD759U"
    sharedSecret = "116128c016cf380933c4b40ffeee8ef5999167f5c3d49298ba2ebfd0502e74e3"
    hashedAuth = "V2P1nwhoENIi7SqkNBuRFcoc8daWd_iWYYDh_0Z01rs"

    expectedClientPrivate = 23358993843321586343730535064475550841207121451219886707870385800362784513137
    expectedServerTempPrivate = 78133010100615632811797373657415808006086410608737048189569410094259232458313

    def decode_base64(self, data):
        return base64.urlsafe_b64decode(base64_add_padding(data).encode("utf-8"))

    def test(self):
        clientPrivate = KeyPair(ldec(self.decode_base64(self.clientPrivate)))
        self.assertEqual(clientPrivate.private_key, self.expectedClientPrivate)
        clientPublic = clientPrivate.get_public_key()
        expectedClientPublic = decode(secp256r1, self.decode_base64(self.clientPublic))
        self.assertEqual(clientPublic, expectedClientPublic)

        serverTempPrivate = KeyPair(ldec(self.decode_base64(self.serverTempPrivate)))
        self.assertEqual(serverTempPrivate.private_key, self.expectedServerTempPrivate)
        serverTempPublic = serverTempPrivate.get_public_key()
        expectedServerTempPublic = decode(secp256r1, self.decode_base64(self.serverTempPublic))
        self.assertEqual(serverTempPublic, expectedServerTempPublic)

        sharedSecret = clientPrivate.generate_shared_secret(serverTempPublic).x
        auth = "0000".encode("utf-8") + sharedSecret
        hashedAuth = base64.urlsafe_b64encode(hashlib.sha256(auth).digest())
