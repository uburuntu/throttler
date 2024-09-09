
from async_flow_control.util.exception import ThrottlerInvArg
from async_flow_control.util import TaskSpacer, DummySpacer
from async_flow_control import AsyncThrottler, RateAsyncThrottler, ConcurrencyAsyncThrottler

import pytest


def test100_err():
    with pytest.raises(ThrottlerInvArg) as e:
        AsyncThrottler()
    assert "need one of rate or concurrency or space" == str(e.value)


def test110_err():
    with pytest.raises(ThrottlerInvArg) as e:
        AsyncThrottler(rate_limit=10, concurrency_limit=2)
    assert "rate/concurrency/space are not compatible" == str(e.value)


def test200_rate():
    at = AsyncThrottler(rate_limit=10)
    assert isinstance(at, RateAsyncThrottler)


def test210_concurrency():
    at = AsyncThrottler(concurrency_limit=10)
    assert isinstance(at, ConcurrencyAsyncThrottler)


def test220_space():
    at = AsyncThrottler(task_space=2)
    assert isinstance(at, TaskSpacer)


def test220_dummy():
    at = AsyncThrottler(task_space=2, dummy=True)
    assert isinstance(at, DummySpacer)
