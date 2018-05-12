from setuptools import setup

setup(
    name="dslink",
    version="0.7.2",
    description="DSLink SDK for Python",
    url="http://github.com/IOT-DSA/sdk-dslink-python",
    author="Logan Gorence",
    author_email="Logan.Gorence@AcuityBrands.com",
    license="Apache 2.0",
    packages=[
        "dslink",
        "dslink.rubenesque",
        "dslink.rubenesque.codecs",
        "dslink.rubenesque.curves",
        "dslink.rubenesque.signatures",
    ],
    install_requires=[
        "autobahn == 0.15.0",
        "requests == 2.10.0",
        "zope.interface == 4.2.0",
        "Twisted == 16.3.0",
        "msgpack-python == 0.4.8",
        "pyOpenSSL == 17.5.0"
    ],
    use_2to3=True
)
