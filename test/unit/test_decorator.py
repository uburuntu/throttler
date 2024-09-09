
import time
import asyncio

from async_flow_control.decorator import throttle, task_spacer, task_spacer_async, timer, timer_async

import pytest


class PrintDestination:

    def __init__(self):
        self.data = []

    def __call__(self, s):
        self.data.append(s)


PRINT = PrintDestination()


# ---------------------------------------------------------------------------


@throttle(rate_limit=5)
async def rate_throttle(v, wait=0.05):
    await asyncio.sleep(wait)
    return v

@task_spacer(period=0.2)
def spacer(v, wait=0.05):
    time.sleep(wait)
    return v

@task_spacer_async(period=0.2)
async def spacer_async(v, wait=0.05):
    await asyncio.sleep(wait)
    return v

@timer(print_func=PRINT)
def do_something(v, wait=0.05):
    time.sleep(wait)
    return v

@timer_async(print_func=PRINT)
async def do_something_async(v, wait=0.05):
    await asyncio.sleep(wait)
    return v

# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test100_throttle():

    start = time.monotonic()
    got = await asyncio.gather(*[rate_throttle(i) for i in range(10)])
    elapsed = time.monotonic() - start

    assert [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] == got

    exp_min = 0.20*9 + 0.05
    assert elapsed > exp_min
    assert elapsed < exp_min + 0.05


def test200_spacer():

    start = time.monotonic()
    for i in range(10):
        spacer(i)
    elapsed = time.monotonic() - start

    exp_min = 0.20*9 + 0.05
    assert elapsed > exp_min
    assert elapsed < exp_min + 0.05


@pytest.mark.asyncio
async def test210_spacer():

    start = time.monotonic()
    for i in range(10):
        await spacer_async(i)
    elapsed = time.monotonic() - start

    exp_min = 0.20*9 + 0.05
    assert elapsed > exp_min
    assert elapsed < exp_min + 0.05


def test300_timer():

    PRINT.data = []
    for i in range(3):
        do_something(i)
    exp = [
        'Timer | elapsed: 0.05 s',
        'Timer | elapsed: 0.05 s',
        'Timer | elapsed: 0.05 s'
    ]
    assert PRINT.data == exp


@pytest.mark.asyncio
async def test310_timer_async():

    PRINT.data = []
    for i in range(3):
        await do_something_async(i)
    exp = [
        'Timer | elapsed: 0.05 s',
        'Timer | elapsed: 0.05 s',
        'Timer | elapsed: 0.05 s'
    ]
    assert PRINT.data == exp
