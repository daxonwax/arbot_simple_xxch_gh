import time as TM
from functools import wraps


class Decoratorkit(object):
    @classmethod
    def print_timing(self, func):
        """
        create a timing decorator function
        use
        @print_timing
        just above the function you want to time
        """

        @wraps(func)  # improves debugging
        def wrapper(*arg, **kwarg):
            start = TM.perf_counter()  # needs python3.3 or higher
            result = func(*arg, **kwarg)
            end = TM.perf_counter()
            fs = "{} took {:.3f} microseconds\n"
            print(fs.format(func.__name__, (end - start) * 1000000))
            return result

        return wrapper
