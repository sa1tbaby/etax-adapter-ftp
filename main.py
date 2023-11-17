from dataclasses import dataclass
from pydantic import BaseModel


class Test1:

    @dataclass
    class Test2:
        test3: str = '2'
        test5: str = '3'

    def test4(self, **argss):
        print(self.Test2.test3)

ss = Test1()

ss.test4(test3='val3', test5='val5')
print(ss.Test2.test3)
