import asyncio

import pytest

from tests.service import BanException, Service, ServiceSimultaneous


class TestService:
    @pytest.mark.parametrize(("rate_limit", "period"), ((1, 0.5), (3, 1.0), (100, 1.5)))
    def test_service(self, rate_limit: int, period: float):
        s = Service(rate_limit, period)

        async def request(value: float):
            return await s.get(value)

        async def run():
            await asyncio.gather(
                *[request(v) for v in range(int(rate_limit / period) + 100)]
            )

        with pytest.raises(BanException):
            asyncio.run(run())

    @pytest.mark.parametrize(("max_simultaneous",), ((1,), (3,), (100,)))
    def test_service_simultaneous(self, max_simultaneous: int):
        s = ServiceSimultaneous(max_simultaneous)

        async def request(value: float):
            return await s.get(value)

        async def run():
            await asyncio.gather(*[request(v) for v in range(max_simultaneous + 100)])

        with pytest.raises(BanException):
            asyncio.run(run())
