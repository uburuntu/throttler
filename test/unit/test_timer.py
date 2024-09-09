
import re
import time
import asyncio

from async_flow_control.timer import Timer

import pytest


class PrintDestination:

    def __init__(self):
        self.data = []

    def __call__(self, s):
        self.data.append(s)


@pytest.mark.asyncio
async def test100():

    d = PrintDestination()
    t = Timer(print_func=d)

    # synchronous
    with t:
        time.sleep(0.1)
    # asynchronous
    with t:
        await asyncio.sleep(0.2)

    exp = [
        'Timer | elapsed: 0.10 s',
        'Timer | elapsed: 0.20 s',
    ]
    assert d.data == exp


@pytest.mark.asyncio
async def test200_name():

    d = PrintDestination()
    t = Timer("unit", print_func=d)

    # synchronous
    with t:
        time.sleep(0.1)
    # asynchronous
    with t:
        await asyncio.sleep(0.2)

    exp = [
        'unit | elapsed: 0.10 s',
        'unit | elapsed: 0.20 s',
    ]
    assert d.data == exp


@pytest.mark.asyncio
async def test300_verbose():

    d = PrintDestination()
    t = Timer("unit", verbose=True, print_func=d)

    # synchronous
    with t:
        time.sleep(0.1)
    # asynchronous
    with t:
        await asyncio.sleep(0.2)

    ts = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}"
    expected = [
        r"   #1 \| unit \| begin: " + ts,
        r"   #1 \| unit \|   end: " + ts + ", elapsed: 0.10 s, average: 0.10 s\n",
        r"   #2 \| unit \| begin: " + ts,
        r"   #2 \| unit \|   end: " + ts + ", elapsed: 0.20 s, average: 0.15 s\n"
    ]
    for exp, got in zip(expected, d.data):
        assert re.match(exp, got)
