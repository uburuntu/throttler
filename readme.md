# Throttler

[![Python](https://img.shields.io/badge/Python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg?longCache=true)]()
[![PyPI](https://img.shields.io/pypi/v/throttler.svg)](https://pypi.python.org/pypi/throttler)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/uburuntu/throttler/blob/master/LICENSE)

[![Python Tests](https://github.com/uburuntu/throttler/actions/workflows/tests.yml/badge.svg)](https://github.com/uburuntu/throttler/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/uburuntu/throttler/branch/master/graph/badge.svg)](https://codecov.io/gh/uburuntu/throttler)

Zero-dependency Python package for easy throttling with asyncio support.

> ![Demo](https://i.imgur.com/MyAALZt.gif)


## 🎒 Install

Just
```sh
pip install throttler
```

## 🧪 Development

```sh
uv sync --locked --all-extras --dev
uv run pytest -vl --cov=./ --cov-report=xml
uv run ruff check .
uv run ruff format .
uv run python -m build
```

## 📌 API Overview

This package exposes four context managers and six decorators:

- `Throttler` / `throttle`: rate-limits how often a block or async function can be entered.
- `ThrottlerSimultaneous` / `throttle_simultaneous`: caps how many async calls can run at once.
- `ExecutionTimer` / `execution_timer`: enforces a minimum period between entries by sleeping.
- `Timer` / `timer`: prints timing information, including average duration across iterations.

`Throttler` and `ThrottlerSimultaneous` are **async context managers** and must be used within an event loop.
`ExecutionTimer` and `Timer` support both sync and async usage.

## ✅ Choosing the Right Tool

- Use `Throttler` when you need **rate limiting** (e.g., 10 requests per 1 second).
- Use `ThrottlerSimultaneous` when you need **concurrency limiting** (e.g., at most 5 in-flight tasks).
- Use `ExecutionTimer` when you want **fixed spacing** between iterations (e.g., run a job once per minute).
- Use `Timer` when you want **timing output** for repeated operations.

It is common to combine `Throttler` with `ThrottlerSimultaneous` for APIs that enforce both rate and concurrency.

## 🛠 Usage Examples
All run-ready examples are [here](examples).

### Throttler and ThrottlerSimultaneous
Both are **async context managers**. Use them inside an async function or event loop.

**Throttler**:
> Async context manager that limits how often the block can be entered.

```python
from throttler import Throttler

# Limit to three calls per second
t = Throttler(rate_limit=3, period=1.0)
async with t:
    pass
```
Or
```python
import asyncio

from throttler import throttle

# Limit to three calls per second
@throttle(rate_limit=3, period=1.0)
async def task():
    return await asyncio.sleep(0.1)
```

**ThrottlerSimultaneous**:
> Async context manager that limits concurrent access to a block.

```python
from throttler import ThrottlerSimultaneous

# Limit to five simultaneous calls
t = ThrottlerSimultaneous(count=5)
async with t:
    pass
```
Or
```python
import asyncio

from throttler import throttle_simultaneous

# Limit to five simultaneous calls
@throttle_simultaneous(count=5)
async def task():
    return await asyncio.sleep(0.1)
```

#### Simple Example
```python
import asyncio
import time

from throttler import throttle


# Limit to two calls per second
@throttle(rate_limit=2, period=1.0)
async def task():
    return await asyncio.sleep(0.1)


async def many_tasks(count: int):
    coros = [task() for _ in range(count)]
    for coro in asyncio.as_completed(coros):
        _ = await coro
        print(f'Timestamp: {time.time()}')

asyncio.run(many_tasks(10))
```

Result output:
```text
Timestamp: 1585183394.8141203
Timestamp: 1585183394.8141203
Timestamp: 1585183395.830335
Timestamp: 1585183395.830335
Timestamp: 1585183396.8460555
Timestamp: 1585183396.8460555
...
```

#### API Example

```python
import asyncio
import time

import aiohttp

from throttler import Throttler, ThrottlerSimultaneous


class SomeAPI:
    api_url = 'https://example.com'

    def __init__(self, throttler):
        self.throttler = throttler

    async def request(self, session: aiohttp.ClientSession):
        async with self.throttler:
            async with session.get(self.api_url) as resp:
                return resp

    async def many_requests(self, count: int):
        async with aiohttp.ClientSession() as session:
            coros = [self.request(session) for _ in range(count)]
            for coro in asyncio.as_completed(coros):
                response = await coro
                print(f'{int(time.time())} | Result: {response.status}')


async def run():
    # Throttler can be of any type
    t = ThrottlerSimultaneous(count=5)        # Five simultaneous requests
    t = Throttler(rate_limit=10, period=3.0)  # Ten requests in three seconds

    api = SomeAPI(t)
    await api.many_requests(100)

asyncio.run(run())
```

Result output:
```text
1585182908 | Result: 200
1585182908 | Result: 200
1585182908 | Result: 200
1585182909 | Result: 200
1585182909 | Result: 200
1585182909 | Result: 200
1585182910 | Result: 200
1585182910 | Result: 200
1585182910 | Result: 200
...
```

### ExecutionTimer
> Context manager that enforces a minimum period between entries by sleeping. It is not a rate limiter like `Throttler`. With `align_sleep=True`, it aligns to wall-clock boundaries (e.g. each minute).

```python
import time

from throttler import ExecutionTimer

et = ExecutionTimer(60, align_sleep=True)

while True:
    with et:
        print(time.asctime(), '|', time.time())
```

Or
```python
import time

from throttler import execution_timer

@execution_timer(60, align_sleep=True)
def f():
    print(time.asctime(), '|', time.time())

while True:
    f()
```

Result output:
```text
Thu Mar 26 00:56:17 2020 | 1585173377.1203406
Thu Mar 26 00:57:00 2020 | 1585173420.0006166
Thu Mar 26 00:58:00 2020 | 1585173480.002517
Thu Mar 26 00:59:00 2020 | 1585173540.001494
```

### Timer
> Context manager for pretty printing start, end, elapsed and average times. Elapsed timing uses a monotonic clock, while start/end timestamps are wall-clock time.

```python
import random
import time

from throttler import Timer

timer = Timer('My Timer', verbose=True)

for _ in range(3):
    with timer:
        time.sleep(random.random())
```

Or
```python
import random
import time

from throttler import timer

@timer('My Timer', verbose=True)
def f():
    time.sleep(random.random())

for _ in range(3):
    f()
```

Result output:
```text
#1 | My Timer | begin: 2020-03-26 01:46:07.648661
#1 | My Timer |   end: 2020-03-26 01:46:08.382135, elapsed: 0.73 sec, average: 0.73 sec
#2 | My Timer | begin: 2020-03-26 01:46:08.382135
#2 | My Timer |   end: 2020-03-26 01:46:08.599919, elapsed: 0.22 sec, average: 0.48 sec
#3 | My Timer | begin: 2020-03-26 01:46:08.599919
#3 | My Timer |   end: 2020-03-26 01:46:09.083370, elapsed: 0.48 sec, average: 0.48 sec
```

## 🧠 Behavior Notes

- `Throttler` uses a sliding window. Each entry may sleep until the oldest recorded entry exits the time window.
- `ThrottlerSimultaneous` uses an async semaphore under the hood.
- `ExecutionTimer` uses a monotonic clock for waiting; when `align_sleep=True` it aligns to wall time.
- `Timer` prints elapsed duration per entry and the running average across all entries.

## ⚠️ Error Handling

- `Throttler(rate_limit, period)` requires a positive integer rate and a positive float period.
- `ThrottlerSimultaneous(count)` requires a positive integer count.

These validations raise `ValueError` early so invalid configuration fails fast.


## 💬 Contributing

Contributions, issues and feature requests are welcome! 

## 📝 License

This project is [MIT](https://github.com/uburuntu/throttler/blob/master/LICENSE) licensed.
