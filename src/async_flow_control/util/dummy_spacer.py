
from .base import BaseAsyncThrottler

class DummySpacer(BaseAsyncThrottler):
    """
    Dummy object that provides synchronous and asynchronous context managers
    that do nothing
    """

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
