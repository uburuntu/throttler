# AsyncThrottler

`AsyncThrottler` is a dispatcher class. Depending on its constructor
arguments, it will create either of four objects:
 * `RateAsyncThrottler`: when the `rate_limit` argument is defined
 * `ConcurrenceAsyncThrottler`: when the `concurrency_limit` argument
 is defined
 * `TaskSpacer`: when the `task_space` argument is defined.
 * `DummySpacer`: when `dummy` is `True`.
 
One created, all objects work the same way: they use an async context
manager to encapsulate some task within a time-controlling block:

```Python

thr = AsyncThrottler(...)

async with thr:
   do_busy_things()

```

Tasks within the async context will only start when the timing flow control
policy allows for it; they will be made to wait before that time comes.
Coordination is ensured when using standard asyncio data flow; the objects are
not thread-safe.

The `DummySpacer` is a dummy object that does not do anything, but provides
the same context manager as the other objects. This allows easy suppression
of time limits without the need to modify the code.

`RateAsyncThrottler` and `ConcurrenceAsyncThrottler` are implemented using
[asyncio synchronization primitives] (lock, semaphore). Since those primitives
are assured to be fair, the serialization in those two classes also satisfies
the fairness property, in the sense that the order in which concurrent tasks
are processed is the order in which they arrive to the context manager.

Since `TaskSpacer` does not serialize tasks (see below), fairness considerations
do no apply to it.


## RateAsyncThrottler

A `RateAsyncThrottler` is designed to schedule tasks so that they are
_started_ at most at a maximum rate. For instance, if we create:

```
thr = AsyncThrottler(rate_limit=30)
```

... then context blocks using that object will be ensured to start _at most_
at a rate of 30 per second. If the rate of arrival to the context block is
higher, tasks are made to wait before the block code is started. The net effect is
that one task is allowed to start every `1/rate_limit` seconds.

Note that the object does not control at all when the tasks _terminate_, so if
they take longer to process than the time period set by `rate_limit`, then they
could accumulate.

The class has also some additional optional parameters:
 * `period`: the period (in seconds) over which `rate_limit` is computed. By
   default it is 1 second, but it can be set to any value
 * `max_queue`: used to limit waiting tasks, see below
 * `max_wait`: used to limit waiting tasks, see below
 * `burst`: used to allow "out-of-bound" temporal bursts of tasks that do not
   respect (locally) the rate limit, see below


### Limiting queues

There are two means of capping the number of tasks waiting to be served:
 * If `max_queue` contains a positive number, that will be the maximum number
   of tasks that can stay in the waiting queue before they are granted access.
   Any task arriving when the limit is reached will trigger a
   `QueueSizeExceeded` exception
 * If `max_wait` contains a positive number, that will be the maximum expected
   waiting time of a task when it arrives to the waiting queue (computed by
   multiplying the number of tasks in the queue by the task period). Any task
   arriving with a greater expected waiting time will trigger a
   `WaitTimeExceeded` exception

Both limits can be active at the same time (in that case it might be useful
to use the parent exception `LimitExceeded` to catch both situations).


### Allowing bursts

The `burst` parameter allows taking "credits" for tasks so that they are
allowed to proceed even if the would go over the rate limit, provided those
credits are "paid back" later. The process is like this:
* If the object is created with `burst=10`, then up to 10 tasks can start
  immediately even if they are above the set rate limit.
* Each time a task uses one of the available burst capacity slots, the amount is
  decremented. When it arrives to zero, no burst tasks are allowed, so
  arriving tasks must wait in the normal way.
* Whenever there is unused time in the task schedule (i.e. a task period is not
  consumed) the burst capacity can recover for future bursts (up to the
  maximum allowed in object creation).

So the net effect is that, over the long run, average rate will still be the
one set by `rate_limit`, but there can be short peaks of activity where the
rate goes above that limit.

### Alternative API

In addition to the async context manager, `RateAsyncThrottler` provides
also another entry point: the `wait()` coroutine method, which implements
the same functionality as the context manager. Therefore, the code:

```Python

thr = AsyncThrottler(...)

await thr.wait()
do_busy_things()

```

is another way of ensuring rate control (this variant, however, will _only_
work for the `RateAsyncThrottler` class)


## ConcurrenceAsyncThrottler

A `ConcurrencyAsyncThrottler` is designed to schedule tasks so that a cap is
set on the number of _simultaneous_ processes that are being executed. For
instance, if we create:

```
thr = ConcurrencyAsyncThrottler(concurrency_limit=20)
```

... a maximum of 20 context blocks using that object will be active at the
same time. Any additional task entering a context block will be made to wait
until another one exits the block.


### Timeout

The additional `timeout` argument can be used to set a maximum wait timeout
(given in seconds, possibly fractional) before a task is granted access.

So, for e.g. `timeout=10` a task can be made to wait in the queue (because the
concurrency limit is reached) for up to 10 seconds. When that timeout is
reached, a `ThrottlerTimeout` exception is raised for that task.


### Alternative API

In addition to the async context manager, `ConcurrencyAsyncThrottler` provides
also another entry point: the `run()`method, if passed a coroutine, will execute
it within the time constraints of the object (i.e. the coroutine will be made to
wait if the number of simultaneous tasks exceeds the limit).

An important difference is that in this entry point the timeout value is
computed not only for task waiting time, but also for the task _computing_
time. That is, the timeout checked is the sum of waiting time + processsing
time for the task.


## TaskSpacer

This class ensures that tasks are executed with a given minimum separation from each
other, spacing execution starts according to its `task_space` argument (defined
in seconds).

When the `align` argument is `True`, it will also enforce that executions
start on integer multiples of the `task_space` value.

This object works somehow differently to the other two classes:
 * for spacing to be respected, tasks must be executed _sequentially_ (i.e. start a
   task only when the preceding one has finished). If tasks are launched
   simultaneously, they will all share the **same** time slot.
 * in addition to asynchronous processing, this object can also work with
   standard (synchronous) context managers


[asyncio synchronization primitives]: https://docs.python.org/3/library/asyncio-sync.html
