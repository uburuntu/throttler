import asyncio
import time

from throttler import ExecutionTimer


def example():
    """
    Output will be like:
        Thu Mar 26 00:56:17 2020 | 1585173377.1203406
        Thu Mar 26 00:57:00 2020 | 1585173420.0006166
        Thu Mar 26 00:58:00 2020 | 1585173480.002517
        Thu Mar 26 00:59:00 2020 | 1585173540.001494
    """

    et = ExecutionTimer(60, align_sleep=True)

    while True:
        with et:
            print(time.asctime(), '|', time.time())


def example_async():
    """
    Output will be like:
        Thu Mar 26 00:56:17 2020 | 1585173377.1203406
        Thu Mar 26 00:57:00 2020 | 1585173420.0006166
        Thu Mar 26 00:58:00 2020 | 1585173480.002517
        Thu Mar 26 00:59:00 2020 | 1585173540.001494
    """

    et = ExecutionTimer(60, align_sleep=True)

    async def coro():
        while True:
            async with et:
                print(time.asctime(), '|', time.time())

    asyncio.run(coro())
