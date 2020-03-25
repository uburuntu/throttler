import random
import time

from throttler import Timer


def example():
    """
    Output will be like:
        My Timer | elapsed: 0.85 sec
        My Timer | elapsed: 0.93 sec
        My Timer | elapsed: 0.31 sec
    """

    timer = Timer('My Timer')

    for _ in range(3):
        with timer:
            time.sleep(random.random())


def example_verbose():
    """
    Output will be like:
        #1 | My Timer | begin: 2020-03-26 01:46:07.648661
        #1 | My Timer |   end: 2020-03-26 01:46:08.382135, elapsed: 0.73 sec, average: 0.73 sec
        #2 | My Timer | begin: 2020-03-26 01:46:08.382135
        #2 | My Timer |   end: 2020-03-26 01:46:08.599919, elapsed: 0.22 sec, average: 0.48 sec
        #3 | My Timer | begin: 2020-03-26 01:46:08.599919
        #3 | My Timer |   end: 2020-03-26 01:46:09.083370, elapsed: 0.48 sec, average: 0.48 sec
    """

    timer = Timer('My Timer', verbose=True)

    for _ in range(3):
        with timer:
            time.sleep(random.random())
