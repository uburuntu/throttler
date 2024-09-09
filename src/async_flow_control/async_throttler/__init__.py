"""
Dispatcher class
"""

from typing import Union

from ..util.exception import ThrottlerInvArg
from ..util.base import BaseAsyncThrottler
from ..util.dummy_spacer import DummySpacer
from ..util.task_spacer import TaskSpacer
from .throttler_rate import RateAsyncThrottler
from .throttler_concurrency import ConcurrencyAsyncThrottler


class AsyncThrottler:

    def __new__(cls, rate_limit: int = None, period: Union[int, float] = None,
                max_queue: int = None, max_wait: float = None, burst: int = None,
                concurrency_limit: int = None, timeout: float = None,
                task_space: float = None, align: bool = None,
                dummy: bool = False, **kwargs) -> BaseAsyncThrottler:
        """
        Instantiate the appropriate spacing object
        """

        if dummy is True:
            return DummySpacer()

        r = rate_limit is not None
        c = concurrency_limit is not None
        s = task_space is not None
        if r + c + s > 1:
            raise ThrottlerInvArg("rate/concurrency/space are not compatible")
        elif r + c + s == 0:
            raise ThrottlerInvArg("need one of rate or concurrency or space")
        elif r:

            if timeout is not None:
                raise ThrottlerInvArg("timeout not supported for RateThrottler")
            if align is not None:
                raise ThrottlerInvArg("align not supported for RateThrottler")
            return RateAsyncThrottler(rate_limit, period=period,
                                      max_queue=max_queue, max_wait=max_wait,
                                      burst=burst, **kwargs)

        else:

            n = "ConcurrencyThrottler" if c else "TaskSpacer"

            if period is not None:
                raise ThrottlerInvArg("period not supported for " + n)
            if max_queue is not None:
                raise ThrottlerInvArg("max_queue not supported for " + n)
            if max_wait is not None:
                raise ThrottlerInvArg("max_wait not supported for " + n)
            if burst is not None:
                raise ThrottlerInvArg("burst not supported for " + n)

            if s and timeout:
                raise ThrottlerInvArg("timeout not supported for " + n)
            if c and align:
                raise ThrottlerInvArg("align not supported for " + n)

            if c:
                return ConcurrencyAsyncThrottler(concurrency_limit,
                                                 timeout=timeout, **kwargs)
            else:
                return TaskSpacer(task_space, align=align, **kwargs)
