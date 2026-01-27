from functools import wraps
from typing import Callable
import inspect

from .execution_timer import ExecutionTimer
from .throttler import Throttler
from .throttler_simultaneous import ThrottlerSimultaneous
from .timer import Timer


def throttle(rate_limit: int, period: float = 1.0):
    """
    Decorator for limiting how often an async function can be entered.

    Args:
        rate_limit: Maximum number of calls per period.
        period: Time window in seconds.
    """

    def decorator(func):
        throttler = Throttler(rate_limit, period)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with throttler:
                return await func(*args, **kwargs)

        return wrapper

    return decorator


def throttle_simultaneous(count: int):
    """
    Decorator for limiting concurrent access to an async function.

    Args:
        count: Maximum number of simultaneous calls.
    """

    def decorator(func):
        throttler = ThrottlerSimultaneous(count)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with throttler:
                return await func(*args, **kwargs)

        return wrapper

    return decorator


def execution_timer(period: float = 60.0, align_sleep: bool = False):
    """
    Decorator that enforces a minimum period between function entries.

    This is not a rate limiter like Throttler. With align_sleep=True, it aligns
    to wall-clock boundaries (e.g. each minute).

    Supports both sync and async callables.
    """

    def decorator(func):
        et = ExecutionTimer(period, align_sleep)

        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def wrapper(*args, **kwargs):
                async with et:
                    return await func(*args, **kwargs)

        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                with et:
                    return func(*args, **kwargs)

        return wrapper

    return decorator


def execution_timer_async(period: float = 60.0, align_sleep: bool = False):
    """
    Async decorator that enforces a minimum period between function entries.

    This is not a rate limiter like Throttler. With align_sleep=True, it aligns
    to wall-clock boundaries (e.g. each minute).

    Backwards compatibility note: execution_timer() now supports async callables.
    """

    def decorator(func):
        et = ExecutionTimer(period, align_sleep)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with et:
                return await func(*args, **kwargs)

        return wrapper

    return decorator


def timer(name: str = None, verbose: bool = False, print_func: Callable = None):
    """
    Decorator for printing elapsed timing information around a function.

    Elapsed timing uses a monotonic clock, while start/end timestamps are wall time.

    Supports both sync and async callables.
    """

    def decorator(func):
        t = Timer(name, verbose, print_func)

        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def wrapper(*args, **kwargs):
                with t:
                    return await func(*args, **kwargs)

        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                with t:
                    return func(*args, **kwargs)

        return wrapper

    return decorator


def timer_async(name: str = None, verbose: bool = False, print_func: Callable = None):
    """
    Async decorator for printing elapsed timing information around a function.

    Elapsed timing uses a monotonic clock, while start/end timestamps are wall time.

    Backwards compatibility note: timer() now supports async callables.
    """

    def decorator(func):
        t = Timer(name, verbose, print_func)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            with t:
                return await func(*args, **kwargs)

        return wrapper

    return decorator
