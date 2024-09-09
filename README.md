# Async Flow Control

[![Python](https://img.shields.io/badge/Python-3.8%20%7C%203.10%20%7C%203.12-blue.svg?longCache=true)]()
[![PyPI](https://img.shields.io/pypi/v/async-flow-control.svg)](https://pypi.python.org/pypi/assign-flow-control)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python Tests](https://github.com/paulovn/async-flow-control/actions/workflows/async-flow-control-PR.yml/badge.svg)](https://github.com/paulovn/async-flow-control/actions/workflows/async-flow-control-PR.yml)

Distribute task execution across time in an asyncio environment, so as to apply
flow control policies.

This started as a fork of [throttler]. It has now diverged heavily from it in some
parts, but its main purpose is still to provide tools that allow to control the
execution of coroutines across time, limiting by different criteria (e.g. task rate
or concurrent execution).


## Install

Just
```sh
pip install async-flow-control
```
The package has no dependencies.


## Usage

The main entry point is the [`AsyncThrottler`] class. This is a dispatcher
class, and will instantiate the appropriate class that controls execution by
either:
 * ensuring it is limited to a maximum task rate, or
 * ensured it is limited to a maximum number of simultaneous processes, or
 * ensured there is a minimum space between task executions.

The main API to use the created objects is by enclosing task execution inside the
async context manager given by the object. This procedure will work for any of
the instantiated classes (some classes have also their own alternative methods).


## Decorators

In addition to the class-based context manager, the same functionality is also
available via a set of [function decorators] that can be used to wrap task
execution and impose the limits.


## Logging

All classes can perform [logging] of waiting times, by using additional
arguments in their constructors.


## Timer

As complementary functionality, a [`Timer`] class can be used to wrap processing
blocks and compute execution time. It also provides a decorator.


## License

This project uses the [MIT](LICENSE) license, the same as the [throttler] project.

[`AsyncThrottler`]: doc/async_throttler.md
[function decorators]: doc/decorators.md
[`Timer`]: doc/timer.md
[logging]: doc/logging.md
[throttler]: https://github.com/uburuntu/throttler
