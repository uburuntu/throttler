import asyncio


class ThrottlerSimultaneous:
    """
    Async context manager that limits concurrent access to a block.

    Example usages:
        - https://github.com/uburuntu/throttler/blob/master/examples/example_throttlers.py
        - https://github.com/uburuntu/throttler/blob/master/examples/example_throttlers_aiohttp.py
    """

    __slots__ = ("_count", "_semaphore")

    def __init__(self, count: int):
        if not (isinstance(count, int) and count > 0):
            raise ValueError("`count` should be positive integer")

        self._count = count
        self._semaphore = None

    async def __aenter__(self):
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self._count)
        await self._semaphore.acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._semaphore.release()
