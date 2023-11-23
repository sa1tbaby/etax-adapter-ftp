import logging
from service.app import start_app
from multiprocessing import Process, Queue
from time import sleep, time
from utils.Models import ServiceSettings, Routes, FtpConnection
from utils.func import script_status, log_rotate
from utils.Decorators import AdditionalTimer
from service import settings, route, ftp_connection, CR_DATE, LOGGER_SETTINGS

log_app = logging.getLogger('__main__')

try:

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

    try:

        main_process = Process()
        func_list = dict()

        @AdditionalTimer(SETTINGS.model_dump(), func_list)
        def app_restart_timer():

            log_app.info('app_restart_timer was triggerd '
                         'current process will be terminate and restart')

            main_process.terminate()

        while True:

            if not script_status(process=main_process, status_queue=APP_STATUS_QUEUE):

                main_process.close()

                if log_rotate(
                        create_date=CR_DATE,
                        tiggering_time=SETTINGS.log_rotate_timer,
                        file_name=LOGGER_SETTINGS.filename
                ):
                    log_app.info('Log file was create a one week ago, logs will be rotated')

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

            app_restart_timer()

            log_app.info(f'The next iteration in __main__ has been postponed for {SETTINGS.main_health_check_timer}sec')
            sleep(SETTINGS.main_health_check_timer)
    except:
        log_app.critical('Caught global exception from __main__ scope during health check loop')
        raise

if __name__ == '__main__':

    main()

