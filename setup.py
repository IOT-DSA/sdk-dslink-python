from setuptools import setup

setup(
    name="dslink-sdk",
    version="0.0.1",
    description="DSLink SDK for Python",
    url="http://github.com/IOT-DSA/sdk-dslink-python",
    author="Logan Gorence",
    author_email="loganjohngorence@gmail.com",
    license="Apache 2.0",
    packages=[
        "sdk"
    ],
    install_requires=[
        "pyelliptic",
        "requests"
    ]
)
