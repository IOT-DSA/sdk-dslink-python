from setuptools import setup

setup(
    name="dslink",
    version="0.1.4",
    description="DSLink SDK for Python",
    url="http://github.com/IOT-DSA/sdk-dslink-python",
    author="Logan Gorence",
    author_email="l.gorence@dglogik.com",
    license="Apache 2.0",
    packages=[
        "dslink"
    ],
    install_requires=[
        "asyncio",
        "autobahn",
        "pyelliptic",
        "requests",
        "zope.interface"
    ]
)
