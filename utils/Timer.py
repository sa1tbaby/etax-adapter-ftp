import time


class Timer:

    def __init__(self,
                 name: str,
                 loger):

        self.loger_timer = loger.getLogger(name)
        self.__timers_list = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'state'):
            cls.state = super(Timer, cls).__new__(cls)
        return cls.state

    def create_timer(self, timer_name):

        if type(timer_name) is str:
            self.__timers_list.setdefault(timer_name, str(time.perf_counter()))

        if type(timer_name) is list:
            for item in timer_name:
                self.__timers_list.setdefault(item, str(time.perf_counter()))
                self.loger_timer.debug(f'timer {item}: successfully init')

        self.loger_timer.info(f'timers {self.__timers_list.keys()}: successfully init')
        return True

    def timer(self, timer_delay: int, timer_name: str):

        if round( time.perf_counter() - float(self.__timers_list[timer_name]), 2 ) > int(timer_delay):
            self.__timers_list[timer_name] = str(time.perf_counter())
            self.loger_timer.info(f'timer {timer_name}: was triggered, start time has been overwrite')
            return True

        return False

    @property
    def count(self):
        return self.__timers_list.keys()