import asyncio
import time

from typing import Callable

from .base import BaseAsyncThrottler
from .exception import ThrottlerInvArg


class TaskSpacer(BaseAsyncThrottler):
    """
    Synchronous and asynchronous context managers to spread across time the access
    time to a context block.
    It either:
      - waits `task_space` secs between each access,
      - or aligns accesses to multiples of the time period

    It will only work with strictly sequential context blocks
    """
    __slots__ = ('_period', '_align_sleep', '_start_time', '_next_time')


    def __init__(self, task_space: float = 1.0, align: bool = False,
                 logger: Callable = None, log_msg: str = None):
        """
          :param task_space: time (seconds) that tasks should be spaced
          :param align: align executions to integer multiples of task_space
          :param logger: a callable that will be used to log waiting times
          :param log_msg: logging message to send to the callable
        """
        if not isinstance(task_space, (float, int)) or task_space <= 0:
            raise ThrottlerInvArg("`task_space` must be a positive value")
        self._period = task_space
        self._align_sleep = align

        self._start_time = 0.0
        self._next_time = 0.0

        self._log = logger
        self._log_msg = log_msg or "TaskSpacer: wait %.3f"

    # ----------------------------------------------------------------


    def _start(self):
        curr_time = time.monotonic()
        diff = self._next_time - curr_time
        return diff

    def _exit(self):
        next_time = self._start_time + self._period
        if self._align_sleep:
            next_time -= self._start_time % self._period
        self._next_time = next_time

    # ----------------------------------------------------------------


    def __enter__(self):
        diff = self._start()
        if diff > 0.0:
            if self._log:
                self._log(self._log_msg, diff)
            time.sleep(diff)
        self._start_time = time.monotonic()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._exit()

    # ----------------------------------------------------------------


    async def __aenter__(self):
        diff = self._start()
        if diff > 0.0:
            if self._log:
                self._log(self._log_msg, diff)
            await asyncio.sleep(diff)
        self._start_time = time.monotonic()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._exit()
