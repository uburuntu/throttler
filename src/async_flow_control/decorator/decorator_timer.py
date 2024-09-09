from functools import wraps
from typing import Callable

from ..timer import Timer



def timer(name: str = None, verbose: bool = False, print_func: Callable = None):
    def decorator(func):
        t = Timer(name, verbose, print_func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            with t:
                return func(*args, **kwargs)

        return wrapper

    return decorator


def timer_async(name: str = None, verbose: bool = False, print_func: Callable = None):
    def decorator(func):
        t = Timer(name, verbose, print_func)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            with t:
                return await func(*args, **kwargs)

        return wrapper

    return decorator
