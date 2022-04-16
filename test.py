import asyncio
import time


def cofoo():
    return "Return JSON"


def wrap():
    yield "created"
    yield from cofoo()
    time.sleep(5)
    yield "deleted"


print(*wrap())
