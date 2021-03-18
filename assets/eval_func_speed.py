# timer decorators Juanso 2020-12-30
import functools
import time
import logging
import inspect


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def runtime(func):
    """Print the runtime of the decorated function"""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()  # 2
        run_time = (end_time - start_time) * 1000  # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} ms")
        return value

    return wrapper_timer


def runtime_log(func: object) -> object:
    """Print the runtime of the decorated function (using logging)"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()  # 2
        run_time = (end_time - start_time) * 1000  # 3
        currframe = inspect.currentframe()
        callframe = inspect.getouterframes(currframe, 2)
        funcname=callframe[1][4][1].replace('\n', '').strip()
        print(f"{bcolors.OKBLUE} Runtime: {run_time:.4f} ms. {bcolors.OKGREEN}  > {callframe[1][1]} > line: {callframe[1][2]} {bcolors.UNDERLINE} - {funcname} {bcolors.ENDC}")
        return value
    return wrapper_timer


def debug(func):
    """Print the function signature and return value"""
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]  # 1
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
        signature = ", ".join(args_repr + kwargs_repr)  # 3
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {value!r}")  # 4
        return value
    return wrapper_debug


def slow_down(_func=None, *, rate=1):
    """Sleep given amount of seconds before calling the function"""

    def decorator_slow_down(func):
        @functools.wraps(func)
        def wrapper_slow_down(*args, **kwargs):
            time.sleep(rate)
            return func(*args, **kwargs)

        return wrapper_slow_down

    if _func is None:
        return decorator_slow_down
    else:
        return decorator_slow_down(_func)
