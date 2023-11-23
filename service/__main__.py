from service.app import start_app
from multiprocessing import Process, set_start_method, Queue
from time import sleep
from utils.Models import ServiceSettings, Routes, FtpConnection
from utils.func import put_in_queue, script_status
from service import log_app, CONFIG
from os.path import pardir, join

SETTINGS = ServiceSettings()
LISTING_PATHS = Routes()
LISTING_SERVER_QUEUE = Queue()
LISTING_CLIENT_QUEUE = Queue()
APP_STATUS_QUEUE = Queue()
FTP_CONFIG = FtpConnection()
CONNECTION_SSL = False

set_start_method('spawn')
def main():

    main_process = Process()

    while True:

        if not script_status(process=main_process, status_queue=APP_STATUS_QUEUE):

            main_process = Process(
                target=start_app,
                daemon=True,
                args=(SETTINGS,
                      LISTING_PATHS,
                      LISTING_SERVER_QUEUE,
                      LISTING_CLIENT_QUEUE,
                      FTP_CONFIG,
                      CONNECTION_SSL,)
            )

            main_process.start()

        sleep(SETTINGS.main_health_check_timer)


if __name__ == '__main__':
    main()

