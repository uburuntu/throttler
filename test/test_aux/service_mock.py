
import asyncio
from typing import Union

from async_flow_control.util.base import BaseAsyncThrottler
from async_flow_control.util.exception import ThrottlerException

class ServiceMock:
    """
    A mock service to test task execution scheduling
    """

    def __init__(self, throttler: BaseAsyncThrottler, service_time: float = 0.1):
        self.thr = throttler
        self.time = service_time

    async def __call__(self, value: int, wait: float = None,
                       exc: Exception = None) -> Union[int, str]:
        """
        Service execution
        """
        try:
            async with self.thr:
                if exc:
                    raise exc
                await asyncio.sleep(wait or self.time)
                return value
        except ThrottlerException as e:
            return e.__class__.__name__
