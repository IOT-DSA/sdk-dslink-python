from setuptools import setup
import sys

requirements = [
    "autobahn",
    "pyelliptic",
    "requests",
    "twisted",
    "zope.interface"
]

if sys.version_info < (3, 3):
    requirements.append("enum34")

setup(
    name="dslink",
    version="0.5.11",
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
