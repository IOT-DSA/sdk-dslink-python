from setuptools import setup

setup(
    name="dslink",
    python_requires=">3.5.0",
    version="0.8.0",
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
        "websockets == 4.0.1"
        "requests == 2.18.4",
        "msgpack-python == 0.5.6",
        "pyOpenSSL == 17.5.0"
    ]
)
