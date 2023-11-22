import time
from dataclasses import dataclass
from pydantic import BaseModel
from functools import wraps

space = {}


def decor(func):
    def _wrap(*args, **kwargs):

        start = time.time()
        result = func(*args, **kwargs)

        return result, time.time() - start

    return _wrap

class Test1:

    def __init__(self):
        self.counter = None

    @decor
    def asdasf(self, a):

        c = 0

        while c < 100000000000:
            c = a+c

        return c





if __name__ == '__main__':
    ss = Test1()

    asdasd = ss.asdasf(200)


    print(asdasd)




