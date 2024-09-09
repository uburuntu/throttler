"""
Object to enforce a maximum rate of asynchronous tasks.

The general mechanics are:
 * processes are granted access in arrival order
 * a spacing between processes is computed by using rate_limit and period
 * processes are granted access with a minimum spacing as determined above
 * if the minimum spacing has not been achieved, the process is made to wait until
   it can start
 * additional options can impose a limit on waiting time or number of waiting
   processes, or allow short bursts of out-of-band processes
"""

import asyncio
import time
from dataclasses import dataclass

from typing import Union, Callable

from ..util.exception import ThrottlerInvArg, QueueSizeExceeded, WaitTimeExceeded
from ..util.base import BaseAsyncThrottler



@dataclass(frozen=True)
class ThrottleCfg:
    wait: float
    max_q: int = None
    max_w: float = None
    burst: int = None


class RateAsyncThrottler(BaseAsyncThrottler):
    """
    Context manager for limiting rate of accessing to context block.
    """
    __slots__ = ('_cfg', '_queue', '_curr', '_burst', '_margin', '_lock')

    def __init__(self, rate_limit: int, period: Union[int, float] = 1.0,
                 max_queue: int = None, max_wait: float = None, burst: int = None,
                 logger: Callable = None, log_msg: str = None):
        """
          :param rate_limit: maximum number of processes allowed
          :param period: time interval (seconds) to count the rate limit
          :param max_queue: maximum number of processes allowed to stay in the
             queue
          :param max_wait: maximum waiting time in the queue for a processt
          :param burst: number of processes that can be granted access over the
             rate limit
          :param logger: a callable that will be used to log waiting times
          :param log_msg: logging message to send to the callable
        """
        if period is None:
            period = 1.0

        if not (isinstance(rate_limit, int) and rate_limit > 0):
            raise ThrottlerInvArg('`rate_limit` must be a positive integer')
        if not (isinstance(period, (int, float)) and period > 0.):
            raise ThrottlerInvArg('`period` must be a positive float')
        if max_queue is not None and not (isinstance(max_queue, int) and max_queue > 0):
            raise ThrottlerInvArg('`max_queue` must be a positive integer')
        if max_wait is not None and not (isinstance(max_wait, (int, float)) and max_wait > 0.):
            raise ThrottlerInvArg('`max_wait` must be a positive float')
        if burst is not None and not (isinstance(burst, int) and burst > 0):
            raise ThrottlerInvArg('`burst` must be a positive integer')

        # Create config
        self._cfg = ThrottleCfg(float(period)/rate_limit, max_queue,
                                float(max_wait) if max_wait else None, burst)
        #print(self._cfg)

        # Number of processes in the queue
        self._queue = 0
        # Timestamp of the last granted access
        self._curr = 0.0
        # Allowed burst capacity
        self._burst = burst or 0
        # Accumulated margin to be used for bursts
        self._margin = 0.0
        # The lock to be used to serialize task wait time
        self._lock = asyncio.Lock()
        # Logging stuff
        self._log = logger
        self._log_msg = log_msg or "RateThrottler: wait %.3f"


    def _compute_wait(self) -> float:
        """
        Compute the waiting time for a process before it is granted access
        """
        # When does the next time slot come?
        next_ts = self._curr + self._cfg.wait
        wait = next_ts - time.monotonic()
        #print(f" Q{self._queue:2} B{self._burst:2}  W {wait:+.4f} ", end="")

        # If we don't have to wait, return now
        if wait <= 0.0:

            # Before returning, see if we can recover some lost burst capacity
            if self._cfg.burst and self._burst < self._cfg.burst:
                self._margin -= wait
                extra = int(self._margin/self._cfg.wait)
                if extra:
                    self._burst = min(self._burst + extra, self._cfg.burst)
                    self._margin = max(self._margin - extra*self._cfg.wait, 0)

            #  return ok (no wait)
            return 0.0

        # No room. See if we can get an option from the burst capacity
        if self._burst:
            self._burst -= 1
            return 0.0   # no wait

        # We'll have to wait
        return wait


    async def wait(self):
        """
        Wait the time needed to abide with the rate policy
        """
        # Check that this request is not above the limits
        if self._cfg.max_q and self._queue > self._cfg.max_q:
            raise QueueSizeExceeded("too many tasks in the queue")
        if self._cfg.max_w and (w := self._cfg.wait*self._queue > self._cfg.max_w):
            raise WaitTimeExceeded(f"expected wait time is too long: {w:.2f}")

        # Serialize access to the object behaviour
        self._queue += 1
        async with self._lock:
            # How much do we need to wait
            wait = self._compute_wait()
            #print(f"   W {wait:+.4f}")
            # Wait if needed
            if wait > 0:
                if self._log:
                    self._log(self._log_msg, wait)
                await asyncio.sleep(wait)
            # Access is granted. Update state
            self._curr = time.monotonic()
            self._queue -= 1

        return self


    async def __aenter__(self):
        await self.wait()
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
