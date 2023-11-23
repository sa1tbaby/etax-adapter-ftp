import logging
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


class AdditionalTimer:

    def __init__(
            self,
            config: dict,
            obj_list: dict,
    ):
        self._log = logging.getLogger('AdditionalTimer')
        self.config = config
        self.obj_list = obj_list

    def __call__(self, func):

        try:

            @wraps(func)
            def _wrapper(*args, **kwargs):

                start_time = time()
                deta_t = start_time - self.obj_list.setdefault(func.__name__, start_time)

                self._log.debug(f'func_name={func.__name__}, '
                                f'delta_time={deta_t}, '
                                f'triggering_time={self.config.get(func.__name__)}')

                if deta_t > self.config.get(func.__name__):

                    self.obj_list.update({func.__name__: start_time})
                    self._log.debug(f'Timer for function={func.__name__}, was triggered '
                                    f'call time in list for cur func was overwritten '
                                    f'cur_time={start_time}')

                    result = func(*args, **kwargs)

                else:

                    result = False

                return result

        except:
            self._log.critical('Caught global exception during __call__ from AdditionalTimer', exc_info=True)
            raise

        else:

            return _wrapper






