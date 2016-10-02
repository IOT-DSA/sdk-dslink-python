from setuptools import setup

setup(
    name="dslink",
    version="0.6.23",
    description="DSLink SDK for Python",
    url="http://github.com/IOT-DSA/sdk-dslink-python",
    author="Logan Gorence",
    author_email="l.gorence@dglogik.com",
    license="Apache 2.0",
    packages=[
        "dslink",
    ],
    install_requires=[
        "autobahn == 0.15.0",
        "pyelliptic == 1.5.7",
        "requests == 2.10.0",
        "zope.interface == 4.2.0",
        "Twisted == 16.3.0"
    ],
    use_2to3=True
)
