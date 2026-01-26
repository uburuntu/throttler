import asyncio
import time


class ExecutionTimer:
    """
    Context manager for time limiting of accessing to context block.
    Simply sleep `period` secs before next accessing, not analog of Throttler.
    Also it can align to start of minutes.

    Example usage:
        - https://github.com/uburuntu/throttler/blob/master/examples/example_execution_timer.py
    """

    __slots__ = (
        "_period",
        "_align_sleep",
        "_start_time",
        "_next_time",
        "_start_wall",
    )

    def __init__(self, period: float = 60.0, align_sleep: bool = False):
        self._period = period
        self._align_sleep = align_sleep

        self._start_time = 0.0
        self._next_time = 0.0
        self._start_wall = 0.0

    def _start(self):
        curr_time = time.monotonic()
        diff = self._next_time - curr_time
        return diff

    def _exit(self):
        if self._align_sleep:
            next_wall = self._start_wall + self._period
            next_wall -= self._start_wall % self._period
            wall_now = time.time()
            delay = max(0.0, next_wall - wall_now)
            self._next_time = time.monotonic() + delay
        else:
            self._next_time = self._start_time + self._period

    def __enter__(self):
        diff = self._start()
        if diff > 0.0:
            time.sleep(diff)
        self._start_time = time.monotonic()
        self._start_wall = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._exit()

    async def __aenter__(self):
        diff = self._start()
        if diff > 0.0:
            await asyncio.sleep(diff)
        self._start_time = time.monotonic()
        self._start_wall = time.time()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._exit()
