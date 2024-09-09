
import time
import asyncio
import pytest
import logging

from async_flow_control import AsyncThrottler

from test_aux.logger_mock import LoggerMock
from test_aux.service_mock import ServiceMock


async def do_nothing(t=0.1):
    start = time.monotonic()
    await asyncio.sleep(t)
    return time.monotonic() - start


# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test200_rate_log():
    log = LoggerMock()
    rt = AsyncThrottler(rate_limit=4, logger=log)

    for n in range(4):
        async with rt:
            await do_nothing()

    exp = [
        'RateThrottler: wait %.3f',
        'RateThrottler: wait %.3f',
        'RateThrottler: wait %.3f'
    ]
    assert log.msg == exp

    exp = [0.15, 0.15, 0.15]
    assert pytest.approx(log.wait, abs=0.001) == exp


@pytest.mark.asyncio
async def test210_rate_log():
    log = LoggerMock()
    rt = AsyncThrottler(rate_limit=4, logger=log, log_msg="UNIT")

    for n in range(4):
        async with rt:
            await do_nothing()

    assert log.msg == ['UNIT','UNIT','UNIT']
    assert pytest.approx(log.wait, abs=0.001) == [0.15, 0.15, 0.15]


@pytest.mark.asyncio
async def test220_rate_log_records(caplog):
    """
    Test log records with an actual loggger
    """
    caplog.set_level(logging.INFO)
    log = logging.getLogger()
    rt = AsyncThrottler(rate_limit=4, logger=log.info)

    for n in range(4):
        async with rt:
            await do_nothing()

    exp = ('root', logging.INFO, 'RateThrottler: wait 0.150')
    got = caplog.record_tuples
    assert got == [exp, exp, exp]


@pytest.mark.asyncio
async def test300_concurrency_log():
    log = LoggerMock()
    rt = AsyncThrottler(concurrency_limit=5, logger=log)
    s = ServiceMock(rt, service_time=0.1)
    await asyncio.gather(*[s(i) for i in range(6)])

    exp = [
        'ConcurrencyThrottler: wait %.3f',
        'ConcurrencyThrottler: wait %.3f',
        'ConcurrencyThrottler: wait %.3f',
        'ConcurrencyThrottler: wait %.3f',
        'ConcurrencyThrottler: wait %.3f',
        'ConcurrencyThrottler: wait %.3f'
    ]
    assert log.msg == exp

    exp = [0, 0, 0, 0, 0, 0.1]
    assert pytest.approx(log.wait, abs=0.001) == exp


@pytest.mark.asyncio
async def test320_rate_log_records(caplog):
    """
    Test log records with an actual loggger
    """
    caplog.set_level(logging.INFO)
    log = logging.getLogger()

    rt = AsyncThrottler(concurrency_limit=5, logger=log.info)
    s = ServiceMock(rt, service_time=0.1)
    await asyncio.gather(*[s(i) for i in range(6)])

    exp = [
        ('root', logging.INFO, 'ConcurrencyThrottler: wait 0.000'),
        ('root', logging.INFO, 'ConcurrencyThrottler: wait 0.000'),
        ('root', logging.INFO, 'ConcurrencyThrottler: wait 0.000'),
        ('root', logging.INFO, 'ConcurrencyThrottler: wait 0.000'),
        ('root', logging.INFO, 'ConcurrencyThrottler: wait 0.000'),
        ('root', logging.INFO, 'ConcurrencyThrottler: wait ')
    ]

    got = caplog.record_tuples

    last_wait = float(got[5][2][-5:])
    assert pytest.approx(0.1, abs=0.0011) == last_wait

    got[5] = (got[5][0], got[5][1], got[5][2][:-5])
    assert got == exp


@pytest.mark.asyncio
async def test400_space_log():
    log = LoggerMock()
    at = AsyncThrottler(task_space=0.5, logger=log)
    s = ServiceMock(at, service_time=0.05)
    for i in range(4):
        await s(i)

    exp = [
        'TaskSpacer: wait %.3f',
        'TaskSpacer: wait %.3f',
        'TaskSpacer: wait %.3f'
    ]
    assert log.msg == exp
    assert pytest.approx(log.wait, abs=0.001) == [0.45, 0.45, 0.45]


def test410_space_sync_log():
    log = LoggerMock()
    at = AsyncThrottler(task_space=0.5, logger=log, log_msg="SYNC")
    for i in range(4):
        with at:
            time.sleep(0.05)

    assert log.msg == ['SYNC', 'SYNC', 'SYNC']
    assert pytest.approx(log.wait, abs=0.001) == [0.45, 0.45, 0.45]
