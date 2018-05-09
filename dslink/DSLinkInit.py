import argparse
import asyncio

from .DSLinkHandler import DSLinkHandler


def dslink_start(dslink, args):
    """
    Start DSLink and immediately exit.
    :param dslink: DSLink implementation
    :param args: Command line arguments
    """
    options = parse_args(args)
    handler = DSLinkHandler(dslink, options)
    loop = asyncio.get_event_loop()
    loop.create_task(handler.start())


def dslink_run(dslink, args):
    """
    Start DSLink and block until all tasks have exited/finished.
    :param dslink: DSLink implementation
    :param args: Command line arguments
    """
    options = parse_args(args)
    handler = DSLinkHandler(dslink, options)
    loop = asyncio.get_event_loop()
    loop.create_task(handler.start())
    loop.run_forever()


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--broker", default="http://localhost:8080/conn")
    parser.add_argument("--log", default="info")
    parser.add_argument("--token")
    return parser.parse_args(args)
