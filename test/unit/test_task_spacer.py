import asyncio
import time

import pytest

from async_flow_control.util.exception import ThrottlerInvArg
from async_flow_control.util.task_spacer import TaskSpacer

from test_aux.service_mock import ServiceMock


# ----------------------------------------------------------------------

def test100_err():
    with pytest.raises(ThrottlerInvArg):
        TaskSpacer(-10)


@pytest.mark.asyncio
async def test200_task():
    ts = TaskSpacer(0.2)
    s = ServiceMock(ts, service_time=0.05)
    start = time.monotonic()
    for i in range(10):
        await s(i)
    elapsed = time.monotonic() - start

    # 9 spaces of 0.2, plus the last execution
    exp_min = 0.20*9 + 0.05
    assert elapsed > exp_min
    assert elapsed < exp_min + 0.01


@pytest.mark.asyncio
async def test210_task_align():
    ts = TaskSpacer(0.5, align=True)
    s = ServiceMock(ts, service_time=0.05)
    start = time.monotonic()
    for i in range(4):
        await s(i)
    elapsed = time.monotonic() - start

    # 3 spaces of 0.25, plus the last execution
    exp_min = 0.25*3 + 0.05
    assert elapsed > exp_min


@pytest.mark.asyncio
async def test300_task_simultaneous():
    ts = TaskSpacer(0.5)
    s = ServiceMock(ts, service_time=0.1)
    start = time.monotonic()
    got = await asyncio.gather(*[s(i) for i in range(10)])
    elapsed = time.monotonic() - start

    assert [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] == got

    # Since all al launched simultaneouly, there is no wait time enforced
    exp_min = 0.1
    assert elapsed > exp_min
    assert elapsed < exp_min + 0.05


def test400_task_sync():
    ts = TaskSpacer(0.2)
    start = time.monotonic()
    for i in range(10):
        with ts:
            time.sleep(0.05)
    elapsed = time.monotonic() - start

    # 9 spaces of 0.2, plus the last execution
    exp_min = 0.20*9 + 0.05
    assert elapsed > exp_min
    assert elapsed < exp_min + 0.01
