import asyncio
import time
from collections import deque


class Throttler:
    """
    Context manager for limiting rate of accessing to context block.

    Example usage:
        async def request(t: Throttler):
            async with t:
                return await send_request()

        async def run():
            t = Throttler(rate_limit=500, period=60)

            coros = [request(t) for _ in range(1000)]
            for coro in asyncio.as_completed(coros):
                result = await coro
                print(result)
    """

    def __init__(self, rate_limit: int, period: float = 1.0):
        self.rate_limit = rate_limit
        self.period = period

        self.times = deque()

    async def __aenter__(self):
        while True:
            curr_ts = time.monotonic()
            if len(self.times) < self.rate_limit:
                break

            diff = curr_ts - (self.times[-1] + self.period)
            if diff > 0.:
                self.times.pop()
                break
            await asyncio.sleep(diff)

        self.times.appendleft(curr_ts)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
