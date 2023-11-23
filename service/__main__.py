from service.app import start_app
from multiprocessing import Process, set_start_method, Queue
from time import sleep
from utils.Models import ServiceSettings, Routes, FtpConnection
from utils.func import put_in_queue, script_status
from service import settings, route, ftp_connection, log_app

try:
    #set_start_method('spawn')

    SETTINGS = ServiceSettings(**settings)
    LISTING_PATHS = Routes(**route)
    LISTING_SERVER_QUEUE = Queue()
    LISTING_CLIENT_QUEUE = Queue()
    APP_STATUS_QUEUE = Queue()
    FTP_CONFIG = FtpConnection(**ftp_connection)
    CONNECTION_SSL = False

except:
    log_app.critical('Caught exception in __main__ scope during '
                     'set global parameters',
                     exc_info=True)
    exit(-1073741510)

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
                      APP_STATUS_QUEUE,
                      FTP_CONFIG,
                      CONNECTION_SSL,)
            )

            main_process.start()

        sleep(SETTINGS.main_health_check_timer)


if __name__ == '__main__':
    print(SETTINGS)
    main()

