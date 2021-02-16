import asyncio
from itertools import product

import pytest

from tests.service import Service
from throttler import throttle, Throttler


class TestThrottler:
    @pytest.mark.parametrize(
        ('rate_limit', 'period'),
        tuple(product((-1, 0, '', 1), (-1, -1., 0, 0., '')))
    )
    def test_exceptions(self, rate_limit: int, period: float):
        with pytest.raises(ValueError):
            Throttler(rate_limit, period)

    @pytest.mark.parametrize(
        ('rate_limit', 'period', 'count'),
        tuple(product((1, 3, 5), (0.5, 1.0, 1.5), (3, 5, 7))) +
        tuple(product((100, 1000), (0.5, 1.0, 1.5), (10, 1000)))
    )
    def test_via_service(self, rate_limit: int, period: float, count: int):
        s = Service(rate_limit, period)

        @throttle(rate_limit, period)
        async def request(value: float):
            return await s.get(value)

        main = asyncio.gather(*[request(v) for v in range(count)])
        asyncio.get_event_loop().run_until_complete(main)
