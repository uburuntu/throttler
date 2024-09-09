from time import perf_counter
import asyncio
from collections.abc import Awaitable

from typing import Callable, Dict

from ..util.exception import ThrottlerInvArg, ThrottlerTimeout
from ..util.base import BaseAsyncThrottler



class ConcurrencyAsyncThrottler(BaseAsyncThrottler):
    """
    Object for limiting the simultaneous number of coroutines accessing a context
    block, with the possibility to define a timeout

    Should be created inside of async loop.
    """

    __slots__ = ('_semaphore', '_timeout')

    def __init__(self, concurrency_limit: int, timeout: float = None,
                 logger: Callable = None, log_msg: str = None):
        """
          :param concurrency_limit: maximum number of simultaneous coroutines
          :param timeout: define a timeout to cancel a task, either because
            of waiting in the queue or (if the callable is used) due to processing
            time
          :param logger: a callable that will be used to log waiting times
          :param log_msg: logging message to send to the callable
        """
        if not isinstance(concurrency_limit, int) or concurrency_limit <= 0:
            raise ThrottlerInvArg('`concurrency_limit` must be a positive integer')
        if timeout is not None and not (isinstance(timeout, (int, float)) and timeout > 0.0):
            raise ThrottlerInvArg('`timeout` must be a positive value')

        self._sem = asyncio.Semaphore(concurrency_limit)
        self._timeout = float(timeout) if timeout else None
        self._log = logger
        self._log_msg = log_msg or "ConcurrencyThrottler: wait %.3f"


    async def __aenter__(self):
        """
        Main entry point
        """
        # Log waiting time
        if self._log:
            start = perf_counter()

        # Wait
        try:
            await asyncio.wait_for(self._sem.acquire(), timeout=self._timeout)
        except asyncio.TimeoutError as e:
            raise ThrottlerTimeout(f"timeout exceeded: {self._timeout}") from e
        finally:
            if self._log:
                self._log(self._log_msg, perf_counter() - start)


    async def __aexit__(self, exc_type, exc, tb):
        self._sem.release()


    # ---------------------------------------------------------------------


    async def _run(self, coro: Awaitable):
        async with self._sem:
            return await coro


    async def run(self, coro: Awaitable, log_args: Dict = None):
        """
        Alternative API: execute a coroutine within the concurrency limit
        In this case, the timeout includes both wait time and execution time
        """
        if self._log:
            start = perf_counter()
        try:
            return await asyncio.wait_for(self._run(coro), timeout=self._timeout)
        except asyncio.TimeoutError as e:
            raise ThrottlerTimeout(f"timeout exceeded: {self._timeout}") from e
        finally:
            if self._log:
                self._log(self._log_msg, perf_counter() - start)
