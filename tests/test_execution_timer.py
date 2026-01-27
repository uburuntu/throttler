import os
import time
from math import isclose

import pytest

from throttler import ExecutionTimer, execution_timer, execution_timer_async

# Weak machines may be used for CI, causing delays
ABS_TOL = 0.2 if os.getenv("CI") else 0.1


class TestExecutionTimer:
    @pytest.mark.parametrize("period", (-1, 0, 0.0, "bad"))
    def test_invalid_period(self, period):
        with pytest.raises(ValueError):
            ExecutionTimer(period)

    @pytest.mark.parametrize(("period",), ((1.0,), (3.0,)))
    def test_without_align(self, period: float):
        @execution_timer(period)
        def t():
            curr_ts = time.time()
            if i > 0:
                assert isclose(curr_ts - prev_ts, period, abs_tol=ABS_TOL)
            return curr_ts

        prev_ts = None
        for i in range(3):
            prev_ts = t()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(("period",), ((1.0,), (3.0,)))
    async def test_without_align_via_async_decorator(self, period: float):
        @execution_timer(period)
        async def t():
            curr_ts = time.time()
            if i > 0:
                assert isclose(curr_ts - prev_ts, period, abs_tol=ABS_TOL)
            return curr_ts

        prev_ts = None
        for i in range(3):
            prev_ts = await t()

    @pytest.mark.parametrize(("period",), ((3.0,), (5.0,)))
    def test_with_align(self, period: float):
        @execution_timer(period, align_sleep=True)
        def t():
            curr_ts = time.time()
            if i > 0:
                assert isclose(curr_ts % period, 0.0, abs_tol=ABS_TOL)
                if i > 1:
                    assert isclose(curr_ts - prev_ts, period, abs_tol=ABS_TOL)
            return curr_ts

        prev_ts = None
        for i in range(3):
            prev_ts = t()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(("period",), ((1.0,), (3.0,)))
    async def test_without_align_async(self, period: float):
        @execution_timer_async(period)
        async def t():
            curr_ts = time.time()
            if i > 0:
                assert isclose(curr_ts - prev_ts, period, abs_tol=ABS_TOL)
            return curr_ts

        prev_ts = None
        for i in range(3):
            prev_ts = await t()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(("period",), ((3.0,), (5.0,)))
    async def test_with_align_async(self, period: float):
        @execution_timer_async(period, align_sleep=True)
        async def t():
            curr_ts = time.time()
            if i > 0:
                assert isclose(curr_ts % period, 0.0, abs_tol=ABS_TOL)
                if i > 1:
                    assert isclose(curr_ts - prev_ts, period, abs_tol=ABS_TOL)
            return curr_ts

        prev_ts = None
        for i in range(3):
            prev_ts = await t()
