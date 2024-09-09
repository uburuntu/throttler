from functools import wraps
from typing import Callable

from ..util.task_spacer import TaskSpacer


def task_spacer(period: float = 60., align_sleep: bool = False):
    def decorator(func):
        et = TaskSpacer(period, align_sleep)

        @wraps(func)
        def wrapper(*args, **kwargs):
            with et:
                return func(*args, **kwargs)

        return wrapper

    return decorator


def task_spacer_async(period: float = 60., align_sleep: bool = False):
    def decorator(func):
        et = TaskSpacer(period, align_sleep)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with et:
                return await func(*args, **kwargs)

        return wrapper

    return decorator


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
