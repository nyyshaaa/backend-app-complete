import sys
import asyncio

def pytest_configure():
    if sys.platform.startswith("linux"):
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())