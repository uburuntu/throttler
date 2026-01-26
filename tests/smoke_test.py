import asyncio

from throttler import (
    ExecutionTimer,
    Throttler,
    ThrottlerSimultaneous,
    Timer,
    execution_timer,
    execution_timer_async,
    throttle,
    throttle_simultaneous,
    timer,
    timer_async,
)


def sync_smoke():
    with ExecutionTimer(0.01):
        with Timer("smoke"):
            pass

    @execution_timer(0.01)
    def run():
        return "ok"

    @timer("smoke")
    def run_timer():
        return "ok"

    assert run() == "ok"
    assert run_timer() == "ok"


async def async_smoke():
    throttler = Throttler(1, 0.01)
    async with throttler:
        pass

    throttler_simultaneous = ThrottlerSimultaneous(1)
    async with throttler_simultaneous:
        pass

    @throttle(1, 0.01)
    async def run():
        return "ok"

    @throttle_simultaneous(1)
    async def run_simultaneous():
        return "ok"

    @execution_timer_async(0.01)
    async def run_execution_timer():
        return "ok"

    @timer_async("smoke")
    async def run_timer():
        return "ok"

    assert await run() == "ok"
    assert await run_simultaneous() == "ok"
    assert await run_execution_timer() == "ok"
    assert await run_timer() == "ok"


def main():
    sync_smoke()
    asyncio.run(async_smoke())


if __name__ == "__main__":
    main()
