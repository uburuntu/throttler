import asyncio
import time

import aiohttp

from throttler import Throttler, ThrottlerSimultaneous


class SomeAPI:
    api_url = 'https://example.com'

    def __init__(self, throttler):
        self.throttler = throttler

    async def request(self, session: aiohttp.ClientSession):
        async with self.throttler:
            async with session.get(self.api_url) as resp:
                return resp

    async def many_requests(self, count: int):
        async with aiohttp.ClientSession() as session:
            coros = [self.request(session) for _ in range(count)]
            for coro in asyncio.as_completed(coros):
                response = await coro
                print(f'{int(time.time())} | Result: {response.status}')


def example():
    async def run():
        api = SomeAPI(Throttler(rate_limit=10, period=3.0))
        await api.many_requests(100)

    asyncio.run(run())


def example_simultaneous():
    async def run():
        api = SomeAPI(ThrottlerSimultaneous(count=5))
        await api.many_requests(100)

    asyncio.run(run())
