import asyncio
import time

import pytest

from async_flow_control.util.exception import ThrottlerInvArg
from async_flow_control import RateAsyncThrottler

from test_aux.service_mock import ServiceMock


async def do_nothing(t=0.1):
    start = time.monotonic()
    await asyncio.sleep(t)
    return time.monotonic() - start


# ----------------------------------------------------------------------

def test100_err():
    with pytest.raises(TypeError):
        RateAsyncThrottler()

def test110_err():
    with pytest.raises(ThrottlerInvArg) as e:
        RateAsyncThrottler(-10)
    assert "`rate_limit` must be a positive integer" == str(e.value)

def test120_err():
    with pytest.raises(ThrottlerInvArg) as e:
        RateAsyncThrottler(10, period=0)
    assert "`period` must be a positive float" == str(e.value)


@pytest.mark.asyncio
async def test200_task():
    rt = RateAsyncThrottler(1)
    async with rt:
        r = await do_nothing()
    assert r > 0.1


@pytest.mark.asyncio
async def test210_task():
    rt = RateAsyncThrottler(4)
    start = time.monotonic()
    for n in range(4):
        async with rt:
            await do_nothing()
    elapsed = time.monotonic() - start

    # We wait 3 times 0.25 secs (to comply with the rate limit) plus the
    # execution time of the last task
    exp_time = 3*0.25 + 0.1
    assert elapsed > exp_time
    assert elapsed < exp_time + 0.1


@pytest.mark.asyncio
async def test220_task_period():
    rt = RateAsyncThrottler(8, period=2.0)
    start = time.monotonic()
    for n in range(4):
        async with rt:
            await do_nothing()
    elapsed = time.monotonic() - start

    exp_time = 3*0.25 + 0.1
    assert elapsed > exp_time
    assert elapsed < exp_time + 0.1


@pytest.mark.asyncio
async def test230_task_wait():
    rt = RateAsyncThrottler(8, period=2.0)
    start = time.monotonic()
    for n in range(4):
        await rt.wait()
        await do_nothing()
    elapsed = time.monotonic() - start

    exp_time = 3*0.25 + 0.1
    assert elapsed > exp_time
    assert elapsed < exp_time + 0.1


@pytest.mark.asyncio
async def test250_task():
    rt = RateAsyncThrottler(5)
    s = ServiceMock(rt, service_time=0.05)
    start = time.monotonic()
    got = await asyncio.gather(*[s(i) for i in range(10)])
    elapsed = time.monotonic() - start

    assert [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] == got

    exp_min = 0.20*9 + 0.05
    assert elapsed > exp_min
    assert elapsed < exp_min + 0.05


@pytest.mark.asyncio
async def test300_task_burst():
    rt = RateAsyncThrottler(5, burst=3)
    s = ServiceMock(rt, service_time=0.05)
    start = time.monotonic()
    got = await asyncio.gather(*[s(i) for i in range(10)])
    elapsed = time.monotonic() - start

    assert [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] == got

    exp_min = 0.20*6 + 0.05
    assert elapsed > exp_min
    assert elapsed < exp_min + 0.05


@pytest.mark.asyncio
async def test310_task_burst_recover():
    T = 0.20
    rt = RateAsyncThrottler(int(1/T), burst=3)
    s = ServiceMock(rt, service_time=0.05)

    start = time.monotonic()
    await asyncio.gather(*[s(i) for i in range(10)])
    elapsed = time.monotonic() - start

    exp_min = T*6 + 0.05
    assert elapsed > exp_min
    assert elapsed < exp_min + 0.05

    # Recover some of the burst space by waiting
    await asyncio.sleep(3*T)

    start = time.monotonic()
    await asyncio.gather(*[s(i) for i in range(4)])
    elapsed = time.monotonic() - start

    # We have recovered space for the next task + a burst of 2. So we'll
    # only need to wait for 1 task
    exp_min = T + 0.05
    assert elapsed > exp_min
    assert elapsed < exp_min + 0.05


@pytest.mark.asyncio
async def test400_task_limit():
    rt = RateAsyncThrottler(5, max_queue=4)
    s = ServiceMock(rt, service_time=0.05)

    # This will leave 4 tasks in queue, ok
    got = await asyncio.gather(*[s(i) for i in range(5)])
    assert [0, 1, 2, 3, 4] == got

    # This will leave 5 tasks in queue, over the limit
    got = await asyncio.gather(*[s(i) for i in range(6)])
    assert [0, 1, 2, 3, 4, "QueueSizeExceeded"] == got


@pytest.mark.asyncio
async def test410_task_limit():
    rt = RateAsyncThrottler(4, max_wait=0.99)
    s = ServiceMock(rt, service_time=0.05)

    # This will add 3 tasks to the queue, total wating time 0.25*3 = 0.75
    got = await asyncio.gather(*[s(i) for i in range(4)])
    assert [0, 1, 2, 3] == got

    # This will add 4 tasks to the queue, total waiting time 0.25*5 = 1.00
    got = await asyncio.gather(*[s(i) for i in range(5)])
    assert [0, 1, 2, 3, "WaitTimeExceeded"] == got
