# Timer

A synchronous context manager for pretty printing start, end, elapsed and
average times.

```python
import random
import time

from async_flow_control import Timer

timer = Timer('My Timer', verbose=True)

for _ in range(3):
    with timer:
        time.sleep(random.random())
```

Or, using a decorator:

```python
import random
import time

from async_flow_control import timer

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
