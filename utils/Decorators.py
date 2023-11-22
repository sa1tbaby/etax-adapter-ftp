from time import time, sleep
from functools import wraps

def timekeeper(func):
    @wraps(func)
    def _wrap(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)

        return result, time() - start

    return _wrap


def timer(config: dict, obj_list: dict):
    start_time = time()

    def func_wrap(func):

        delta_t = start_time - obj_list.setdefault(func.__name__, start_time)

        @wraps(func)
        def _wrap(*args, **kwargs):

            if delta_t > config.get(func.__name__):

                obj_list.update(
                    {func.__name__: start_time}
                )

                return func(*args, **kwargs), obj_list

            else:

                return False, obj_list

        return _wrap

    return func_wrap






