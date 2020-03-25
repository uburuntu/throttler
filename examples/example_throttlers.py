import asyncio
import time

from throttler import Throttler, ThrottlerSimultaneous


async def task(throttler):
    async with throttler:
        return await asyncio.sleep(0.1)


async def many_tasks(throttler, count: int):
    coros = [task(throttler) for _ in range(count)]
    for coro in asyncio.as_completed(coros):
        _result = await coro
        print(f'Timestamp: {time.time()}')


def example():
    async def run():
        t = Throttler(rate_limit=10, period=3.0)
        await many_tasks(t, 100)

    asyncio.run(run())


def example_simultaneous():
    async def run():
        t = ThrottlerSimultaneous(count=5)
        await many_tasks(t, 100)

    asyncio.run(run())
