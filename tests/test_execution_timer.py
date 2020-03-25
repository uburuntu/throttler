import time
from math import isclose

import pytest

from throttler import ExecutionTimer


class TestExecutionTimer:
    @pytest.mark.parametrize(
        ('period',), ((1.,), (3.,))
    )
    def test_without_align(self, period: float):
        et = ExecutionTimer(period)
        prev_ts = None
        for i in range(3):
            with et:
                curr_ts = time.time()
                if i > 0:
                    assert isclose(curr_ts - prev_ts, period, abs_tol=0.01)
            prev_ts = curr_ts

    @pytest.mark.parametrize(
        ('period',), ((3.,), (5.,))
    )
    def test_with_align(self, period: float):
        et = ExecutionTimer(period, align_sleep=True)
        prev_ts = None
        for i in range(3):
            with et:
                curr_ts = time.time()
                if i > 0:
                    assert isclose(curr_ts % period, 0., abs_tol=0.01)
                    if i > 1:
                        assert isclose(curr_ts - prev_ts, period, abs_tol=0.01)
            prev_ts = curr_ts

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ('period',), ((1.,), (3.,))
    )
    async def test_without_align_aio(self, period: float):
        et = ExecutionTimer(period)
        prev_ts = None
        for i in range(3):
            async with et:
                curr_ts = time.time()
                if i > 0:
                    assert isclose(curr_ts - prev_ts, period, abs_tol=0.01)
            prev_ts = curr_ts

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ('period',), ((3.,), (5.,))
    )
    async def test_with_align_aio(self, period: float):
        et = ExecutionTimer(period, align_sleep=True)
        prev_ts = None
        for i in range(3):
            async with et:
                curr_ts = time.time()
                if i > 0:
                    assert isclose(curr_ts % period, 0., abs_tol=0.01)
                    if i > 1:
                        assert isclose(curr_ts - prev_ts, period, abs_tol=0.01)
            prev_ts = curr_ts
