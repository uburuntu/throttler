import asyncio

import pytest

from tests.service import BanException, Service, ServiceSimultaneous


class TestService:
    @pytest.mark.parametrize(
        ('rate_limit', 'period'), ((1, 0.5), (3, 1.0), (100, 1.5))
    )
    def test_service(self, rate_limit: int, period: float):
        s = Service(rate_limit, period)

        async def request(value: float):
            return await s.get(value)

        with pytest.raises(BanException):
            main = asyncio.gather(*[request(v) for v in range(int(rate_limit / period) + 100)])
            asyncio.get_event_loop().run_until_complete(main)

    @pytest.mark.parametrize(
        ('max_simultaneous',), ((1,), (3,), (100,))
    )
    def test_service_simultaneous(self, max_simultaneous: int):
        s = ServiceSimultaneous(max_simultaneous)

        async def request(value: float):
            return await s.get(value)

        with pytest.raises(BanException):
            main = asyncio.gather(*[request(v) for v in range(max_simultaneous + 100)])
            asyncio.get_event_loop().run_until_complete(main)
