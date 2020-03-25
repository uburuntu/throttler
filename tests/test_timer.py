import time

import pytest

from throttler import timer, timer_async


class TestTimer:
    @pytest.mark.parametrize(
        ('verbose',), ((True,), (False,))
    )
    def test_simple(self, verbose: bool):
        @timer(name='TestTimer', verbose=verbose)
        def t():
            print(time.time())

        for _ in range(3):
            t()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ('verbose',), ((True,), (False,))
    )
    async def test_simple_async(self, verbose: bool):
        @timer_async(name='TestTimer', verbose=verbose)
        async def t():
            print(time.time())

        for _ in range(3):
            await t()
