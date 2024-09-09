import asyncio
import time

import pytest

from async_flow_control.util.dummy_spacer import DummySpacer


# ----------------------------------------------------------------------


@pytest.mark.asyncio
async def test200_async():
    ds = DummySpacer()
    start = time.monotonic()
    for i in range(5):
        async with ds:
            await asyncio.sleep(0.1)
    elapsed = time.monotonic() - start

    exp_min = 0.10*5
    assert elapsed > exp_min
    assert elapsed < exp_min + 0.01


def test210_sync():
    ds = DummySpacer()
    start = time.monotonic()
    for i in range(5):
        with ds:
            time.sleep(0.1)
    elapsed = time.monotonic() - start

    exp_min = 0.10*5
    assert elapsed > exp_min
    assert elapsed < exp_min + 0.01
