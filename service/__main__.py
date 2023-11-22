from service.app import start_app
from multiprocessing import Process, set_start_method, Queue
from time import sleep
from utils.Models import ServiceSettings, Routes, FtpConnection
set_start_method('spawn')

SETTINGS = ServiceSettings()
LISTING_PATHS = Routes()
LISTING_SERVER_QUEUE = Queue()
LISTING_CLIENT_QUEUE = Queue()
APP_STATUS_QUEUE = Queue()
CONFIG = FtpConnection()
CONNECTION_SSL = False


def script_status(process: Process | bool):
    def check_put(
            queue
    ) -> None:

        tmp = True

        while not queue.empty():
            tmp = queue.get()

        return tmp

    if check_put(APP_STATUS_QUEUE) == 'dead':
        main_log.debug(f'process status dead')
        return False

    else:
        main_log.info(f'process status {process.is_alive()}')
        return process.is_alive()


def main():

    main_process = Process()

    while True:

        if script_status(process=main_process) is False:

            main_process = Process(
                target=start_app,
                daemon=True,
                args=(SETTINGS,
                      LISTING_PATHS,
                      LISTING_SERVER_QUEUE,
                      LISTING_CLIENT_QUEUE,
                      CONFIG,
                      CONNECTION_SSL,)
            )

            main_process.start()

        sleep(SETTINGS.main_health_check_timer)


if __name__ == '__main__':
    main()
