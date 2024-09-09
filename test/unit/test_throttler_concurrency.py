import asyncio
import time

import pytest

from async_flow_control.util.exception import ThrottlerInvArg, ThrottlerTimeout
from async_flow_control import ConcurrencyAsyncThrottler

from test_aux.service_mock import ServiceMock


async def do_nothing_time(wait=0.1):
    start = time.monotonic()
    await asyncio.sleep(wait)
    return time.monotonic() - start


async def do_nothing(v, wait=0.1):
    await asyncio.sleep(wait)
    return v


# ----------------------------------------------------------------------

def test100_err():
    with pytest.raises(TypeError):
        ConcurrencyAsyncThrottler()

def test110_err():
    with pytest.raises(ThrottlerInvArg) as e:
        ConcurrencyAsyncThrottler(-10)
    assert "`concurrency_limit` must be a positive integer" == str(e.value)

def test120_err():
    with pytest.raises(ThrottlerInvArg) as e:
        ConcurrencyAsyncThrottler(10, timeout=0)
    assert "`timeout` must be a positive value" == str(e.value)


@pytest.mark.asyncio
async def test200_task():
    rt = ConcurrencyAsyncThrottler(1)
    async with rt:
        r = await do_nothing_time()
    assert r > 0.1
    assert r < 0.15


@pytest.mark.asyncio
async def test210_task():
    rt = ConcurrencyAsyncThrottler(4)
    start = time.monotonic()
    for n in range(4):
        async with rt:
            await do_nothing(n)
    elapsed = time.monotonic() - start

    # We wait 4 times: one per task. No concurrency wait
    exp_time = 4*0.1
    assert elapsed > exp_time
    assert elapsed < exp_time + 0.05


@pytest.mark.asyncio
async def test220_service():
    rt = ConcurrencyAsyncThrottler(5)
    s = ServiceMock(rt, service_time=0.1)
    start = time.monotonic()
    got = await asyncio.gather(*[s(i) for i in range(5)])
    elapsed = time.monotonic() - start

    assert [0, 1, 2, 3, 4] == got

    # All run at the same time, hence total time is around 0.1
    exp_min = 0.1
    assert elapsed > exp_min
    assert elapsed < exp_min + 0.05


@pytest.mark.asyncio
async def test221_service():
    rt = ConcurrencyAsyncThrottler(5)
    s = ServiceMock(rt, service_time=0.1)
    start = time.monotonic()
    got = await asyncio.gather(*[s(i) for i in range(6)])
    elapsed = time.monotonic() - start

    assert [0, 1, 2, 3, 4, 5] == got

    # This time one task had to wait
    exp_min = 0.20
    assert elapsed > exp_min
    assert elapsed < exp_min + 0.05


@pytest.mark.asyncio
async def test230_task_timeout():
    rt = ConcurrencyAsyncThrottler(4, timeout=0.2)
    s = ServiceMock(rt, service_time=0.1)
    start = time.monotonic()
    got = await asyncio.gather(*[s(i) for i in range(10)])
    elapsed = time.monotonic() - start

    assert [0, 1, 2, 3, 4, 5, 6, 7, 'ThrottlerTimeout', 'ThrottlerTimeout'] == got

    exp_min = 0.20
    assert elapsed > exp_min
    assert elapsed < exp_min + 0.05


@pytest.mark.asyncio
async def test240_exception():
    rt = ConcurrencyAsyncThrottler(10)
    s = ServiceMock(rt, service_time=0.05)

    tasks = [s(i) for i in range(9)]
    tasks.append(s(9, exc=ValueError()))

    with pytest.raises(ValueError):
        await asyncio.gather(*tasks)


@pytest.mark.asyncio
async def test300_run():
    rt = ConcurrencyAsyncThrottler(5)
    start = time.monotonic()
    got = await asyncio.gather(*[rt.run(do_nothing(i)) for i in range(5)])
    elapsed = time.monotonic() - start

    assert [0, 1, 2, 3, 4] == got

    # All run at the same time, hence total time is around 0.1
    exp_min = 0.1
    assert elapsed > exp_min
    assert elapsed < exp_min + 0.05


@pytest.mark.asyncio
async def test310_run():
    rt = ConcurrencyAsyncThrottler(2)
    start = time.monotonic()
    got = await asyncio.gather(*[rt.run(do_nothing(i)) for i in range(5)])
    elapsed = time.monotonic() - start

    assert [0, 1, 2, 3, 4] == got

    # This time they can run simultaneously only in batches of two. So we'll have
    # three batches
    exp_min = 0.3
    assert elapsed > exp_min
    assert elapsed < exp_min + 0.05


@pytest.mark.asyncio
async def test320_run_timeout():
    rt = ConcurrencyAsyncThrottler(2, timeout=0.2)
    with pytest.raises(ThrottlerTimeout) as e:
        await rt.run(do_nothing(0, wait=0.3))

    assert str(e.value) == "timeout exceeded: 0.2"
