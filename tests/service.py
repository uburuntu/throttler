import asyncio
import random
import time
from collections import deque


class BanException(Exception):
    pass


async def sleeper(value: float):
    s = random.uniform(0, 0.1)
    await asyncio.sleep(s)
    return value


class Service:
    def __init__(self, rate_limit: int, period: float):
        self.rate_limit = rate_limit
        self.period = period - 0.01

        self.times = deque((0.,) * rate_limit)

    async def get(self, value: float):
        curr_ts = time.monotonic()
        diff = curr_ts - self.times[0]
        if diff < self.period:
            raise BanException('Limit exceeded')
        self.times.popleft()
        self.times.append(curr_ts)
        return await sleeper(value)


class ServiceSimultaneous:
    def __init__(self, max_simultaneous: int):
        self.max_simultaneous = max_simultaneous

        self.counter = 0

    async def get(self, value: float):
        self.counter += 1
        try:
            if self.counter > self.max_simultaneous:
                raise BanException('Limit exceeded')
            return await sleeper(value)
        finally:
            self.counter -= 1
