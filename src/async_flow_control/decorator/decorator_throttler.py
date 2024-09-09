from functools import wraps
from typing import Callable

from ..async_throttler import AsyncThrottler


def throttle(rate_limit: int = None, period: float = 1.0, max_queue: int = None,
             max_wait: float = None, burst: int = None,
             concurrency_limit: int = None, timeout: float = None):
    """
    Decorator to instantiate and use an AsyncThrottler
    """
    def decorator(func: Callable) -> Callable:

        throttler = AsyncThrottler(
            rate_limit=rate_limit, period=period, max_queue=max_queue,
            max_wait=max_wait, burst=burst,
            concurrency_limit=concurrency_limit, timeout=timeout
        )

        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with throttler:
                return await func(*args, **kwargs)

        return wrapper

    return decorator
