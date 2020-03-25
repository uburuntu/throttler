import asyncio
import time

from throttler.time_manager import TimeManager
from throttler.timer import Timer


def example():
    t = TimeManager(60, align_sleep=True)
    while True:
        with t:
            print(time.asctime(), time.time())


def example_async():
    t = TimeManager(60, align_sleep=True)

    async def coro():
        while True:
            async with t:
                print(time.asctime(), time.time())

    asyncio.run(coro())


def throttler_perf(t, count):
    import aiohttp

    timer = Timer()

    async def request(s):
        async with t:
            async with s.get('https://example.com') as resp:
                return resp.status

    async def run():
        async with aiohttp.ClientSession() as session:
            coros = [request(session) for _ in range(count)]
            for coro in asyncio.as_completed(coros):
                with timer:
                    result = await coro
                    print('      | Result:', result)

    asyncio.run(run())


# throttler_perf(Throttler(rate_limit=300, period=1), 1000)
