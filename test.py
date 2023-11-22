import dataclasses
import time

import pandas

from utils.Decorators import timer
from multiprocessing import Process
class ttt:
    def __init__(self):
        self.tttt = self.SendParams()

    @dataclasses.dataclass
    class SendParams:
        path_client: int = None
        path_server: int = None
        file_name: int = None
        file_size: int = None
        validator: int = None
        destination: int = None

    def ssfas(self, **param):

        asdasdasd = self.SendParams(**param)


        for key, value in param.items():


            self.tttt.__setattr__(key, value)

        print(self.tttt)
        print(asdasdasd)

        #print(self.SendParams.destination)

def test1():

    asdas = ttt()
    param = {
        "validator": 6,
        "file_size": 5,
        "file_name": 4,
        "path_server": 3,
        "path_client": 2,
        "destination": 1,
    }

    asdas.ssfas(validator=6, file_size=5, file_name=4, path_server=3, path_client=2, destination=1)

def test2():
    dict_twasd = dict()
    print(dict_twasd)
    print(dict_twasd.setdefault('value_test', 3))
    print(dict_twasd.setdefault('value_test1', 2))
    dict_twasd.update({'value_test': 2})
    dict_twasd.update({'value_test3': 2})
    print(dict_twasd)
    dict_twasd.update({'value_test3': 88})
    print(dict_twasd)

    print(dict_twasd.get('value_test'))

def test_pandas1():
    j = 10
    data = [
         [i,i+j] for i in range(j)
    ]
    print(data)

    asdasxc = pandas.DataFrame(
        data=data,
        columns=[
            'file_name',
            'file_size'
        ]
    )
    asd = False
    print(asdasxc.count('index'))
    asdasxc=asdasxc.drop(index=2)
    print(asdasxc.count('index'))
    for index, rows in asdasxc.iterrows():
        if not asd:
            print(rows['file_size'])


def test_timer():
    config = {'tets': 15}
    obj_list = dict()
    res = False

    while not res:
        @timer(config=config, obj_list=obj_list)
        def tets(i, j):
            ressss = i * j
            return ressss

        res, obj_list = tets(3, 4)
        print(res, obj_list)
        time.sleep(1)

def test55():

    asdafsas = {
        'a':1,
        'v':2,
        'b':3,

    }

    def aaaas(**kwargs):
        for i in kwargs.items():
            print(i)

    aaaas(**asdafsas)

def test22():
    oass = Process

    print(oass.is_alive())


if __name__ == '__main__':

    test22()

