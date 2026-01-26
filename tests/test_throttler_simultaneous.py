import asyncio

import pytest

from tests.service import ServiceSimultaneous
from throttler import ThrottlerSimultaneous, throttle_simultaneous


class TestThrottlerSimultaneous:
    @pytest.mark.parametrize("count", (0, -1, -5))
    def test_invalid_count(self, count: int):
        with pytest.raises(ValueError):
            ThrottlerSimultaneous(count)

    @pytest.mark.parametrize(
        ("max_simultaneous", "count"), ((1, 10), (3, 10), (100, 500))
    )
    def test_via_service_simultaneous(self, max_simultaneous: int, count: int):
        s = ServiceSimultaneous(max_simultaneous)

        @throttle_simultaneous(max_simultaneous)
        async def request(value: float):
            return await s.get(value)

        async def run():
            await asyncio.gather(*[request(v) for v in range(count)])

        asyncio.run(run())
