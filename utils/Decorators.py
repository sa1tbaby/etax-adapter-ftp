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

        @wraps(func)
        def _wrap(*args, **kwargs):

            delta_t = start_time - obj_list.setdefault(func.__name__, start_time)

            if delta_t > config.get(func.__name__):

                obj_list.update(
                    {func.__name__: start_time}
                )

                return func(*args, **kwargs), obj_list

            else:

                return False, obj_list

        return _wrap

    return func_wrap


class AditionalTimer:

    def __init__(
            self,
            config: dict,
            obj_list: dict,
    ):

        self.config = config
        self.obj_list = obj_list

    def __call__(self, func):

        @wraps(func)
        def _wrapper(*args, **kwargs):

            start_time = time()
            deta_t = start_time - self.obj_list.setdefault(func.__name__, start_time)

            if deta_t > self.config.get(func.__name__):

                self.obj_list.update({func.__name__: start_time})

                result = func(*args, **kwargs)

            else:

                result = False

            return result

        return _wrapper






