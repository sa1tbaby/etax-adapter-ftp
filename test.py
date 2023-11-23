import dataclasses
import time

import pandas

from utils.Decorators import timer, AditionalTimer
from multiprocessing import Process
from os.path import pardir, join, abspath
from json import load
import os


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
    config = {'tets': 3, 'tets2': 6}
    obj_list = dict()
    res = False


    @AditionalTimer(config=config, obj_list=obj_list)
    def tets(i, j):
        ressss = i * j
        return ressss

    @AditionalTimer(config=config, obj_list=obj_list)
    def tets2(i, j):
        ressss = i * j
        return ressss


    while True:

        res = tets(2, 3)
        res2 = tets2(4, 5)
        print(res, res2)
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
    spisok = 'asd,asd,asd'

    spisok = spisok[spisok.find(','):]

    spisok = spisok.split(',')
    print(spisok)

def testttt():
    CONFIG_FILE = ('configs', 'config.json')
    CONFIG_FILE = join(abspath(pardir), CONFIG_FILE[0], CONFIG_FILE[1])

    with open(CONFIG_FILE, 'r') as file:
        config = load(file)

    asdsd = config.get('logger_setting')

    dfffgf = LoggerSettings(**asdsd)
    print(dfffgf)
if __name__ == '__main__':

    testttt()

