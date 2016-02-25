from setuptools import setup

requirements = [
    "autobahn",
    "pyelliptic",
    "requests",
    "twisted",
    "zope.interface"
]

setup(
    name="dslink",
    version="0.6.6",
    description="DSLink SDK for Python",
    url="http://github.com/IOT-DSA/sdk-dslink-python",
    author="Logan Gorence",
    author_email="l.gorence@dglogik.com",
    license="Apache 2.0",
    packages=[
        "dslink"
    ],
    install_requires=requirements,
    use_2to3=True
)
