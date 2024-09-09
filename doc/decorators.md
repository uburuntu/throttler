# Decorators

The functionality provided by [AsyncThrottler], [TaskSpacer] and [Timer]
classes can also be provided via function decorators.

## throttle

The `@throttle` decorator accepts the same arguments as `AsyncThrottler`. It
will instantiate the appropriate class according to those arguments and enfore
flow control on the decorated function. For example:

```Python

from async_flow_control.decorator import throttle

@throttle(rate_limit=5)
async def some_processing(arg1, argX=0.03171):
  some_code
```

... this will ensure that calls to `some_processing()` are executed at a rate
of at most 5 per second.


## task_spacer & task_spacer_async

The `@task_spacer_async` decorator is equivalent to a
`@throttle(task_space=N)` decorator.

The `@task_spacer` decorator does the same, but it decorates regular functions
instead of coroutines.


## timer & timer_async

The `@timer` and `@timer_async` decorators work by instantiating a [`Timer`]
object, in either a synchronous or an asynchronous context.



[AsyncThrottler]: async-throttler.md
[TaskSpacer]: async-throttler.md#task-spacer
[`Timer`]: timer.md
