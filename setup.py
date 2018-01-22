from setuptools import setup

setup(
    name="dslink",
    version="0.7.0",
    description="DSLink SDK for Python",
    url="http://github.com/IOT-DSA/sdk-dslink-python",
    author="Logan Gorence",
    author_email="Logan.Gorence@AcuityBrands.com",
    license="Apache 2.0",
    packages=[
        "dslink",
    ],
    install_requires=[
        "autobahn == 0.15.0",
        "requests == 2.10.0",
        "zope.interface == 4.2.0",
        "Twisted == 16.3.0",
        "msgpack-python == 0.4.8"
    ],
    use_2to3=True
)
