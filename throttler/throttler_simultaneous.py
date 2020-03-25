import asyncio


class ThrottlerSimultaneous:
    """
    Context manager for limiting simultaneous count of accessing to context block.

    Example usage:
        async def request(t: ThrottlerSimultaneous):
            async with t:
                return await send_request()

        async def run():
            t = ThrottlerSimultaneous(count=50)

            coros = [request(t) for _ in range(1000)]
            for coro in asyncio.as_completed(coros):
                result = await coro
                print(result)
    """

    __slots__ = ('semaphore',)

    def __init__(self, count: int):
        self.semaphore = asyncio.Semaphore(count)

    async def __aenter__(self):
        await self.semaphore.acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.semaphore.release()
