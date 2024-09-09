from datetime import datetime
from typing import Callable


class Timer:
    """
    Context manager for pretty printing start, end, elapsed and average times
    """

    def __init__(self, name: str = None, verbose: bool = False,
                 print_func: Callable = None):
        """
          :param name: name to be used in printed lines
          :param verbose: add lines both at start and end of processing, and
            show averages
          :param print_func: alternative callable to send output to
        """
        self.iteration = 1
        self.start_dt = None
        self.elapsed_all = 0.0

        self.name = name or "Timer"
        self.verbose = verbose
        self.print = print_func or print


    def __enter__(self):
        self.start_dt = datetime.now()
        if self.verbose:
            self.print(f'{f"#{self.iteration}":>5} | {self.name} | begin: {self.start_dt}')


    def __exit__(self, exc_type, exc_val, exc_tb):
        curr_dt = datetime.now()
        elapsed = (curr_dt - self.start_dt).total_seconds()

        self.elapsed_all += elapsed
        average = self.elapsed_all / self.iteration

        if self.verbose:
            self.print(f'{f"#{self.iteration}":>5} | {self.name} |   end: {curr_dt}, elapsed: {elapsed:.2f} s, '
                       f'average: {average:.2f} s\n')
        else:
            self.print(f'{self.name} | elapsed: {elapsed:.2f} s')

        self.iteration += 1
