import time

import pytest

from throttler import Timer


class TestTimer:
    @pytest.mark.parametrize(
        ('verbose',), ((True,), (False,))
    )
    def test_simple(self, verbose: bool):
        timer = Timer(name='TestTimer', verbose=verbose)
        for _ in range(3):
            with timer:
                print(time.time())
