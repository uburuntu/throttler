import asyncio
from itertools import product

import pytest

from tests.service import Service
from throttler import Throttler


class TestThrottler:
    @pytest.mark.parametrize(
        ('rate_limit', 'period', 'count'), tuple(product((100, 1000), (0.5, 1.0, 1.5), (10, 1000)))
    )
    def test_via_service(self, rate_limit: int, period: float, count: int):
        s = Service(rate_limit, period)
        t = Throttler(rate_limit, period)

        async def request(value: float):
            async with t:
                return await s.get(value)

        main = asyncio.gather(*[request(v) for v in range(count)])
        asyncio.get_event_loop().run_until_complete(main)
