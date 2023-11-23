import time
import logging
import ServiceClasses

from utils.Models import ServiceSettings, Routes, FtpConnection
from utils.Decorators import AdditionalTimer
from utils.func import put_in_queue

from multiprocessing import Queue


def start_app(
    SETTINGS: ServiceSettings,
    LISTING_PATHS: Routes,
    LISTING_SERVER_QUEUE: Queue,
    LISTING_CLIENT_QUEUE: Queue,
    APP_STATUS_QUEUE: Queue,
    FTP_CONFIG: FtpConnection,
    CONNECTION_SSL
):

    log_app = logging.getLogger('app')

    try:
        func_list = dict()
        put_in_queue(APP_STATUS_QUEUE, 'SLAVE')

        app = ServiceClasses.ServiceSender(
            settings=SETTINGS,
            listing_paths=LISTING_PATHS,
            listing_server_queue=LISTING_SERVER_QUEUE,
            listing_client_queue=LISTING_CLIENT_QUEUE,
            config=FTP_CONFIG,
            connection_ssl=CONNECTION_SSL
        )

        put_in_queue(APP_STATUS_QUEUE, 'IDLE')

        @AdditionalTimer(SETTINGS.model_dump(), func_list)
        def app_dwnld_timer_client():

            put_in_queue(APP_STATUS_QUEUE, 'SLAVE')

            destination = app.MODE_CLIENT
            listing = app.listing_from_server()
            result = app.send_files(destination, listing)

            log_app.info(f'Download files from server was successfully end result={result}')
            put_in_queue(APP_STATUS_QUEUE, 'IDLE')

            return result

        @AdditionalTimer(SETTINGS.model_dump(), func_list)
        def app_dwnld_timer_server():

            put_in_queue(APP_STATUS_QUEUE, 'SLAVE')

            destination = app.MODE_SERVER
            listing = app.listing_from_client()
            result = app.send_files(destination, listing)


            put_in_queue(APP_STATUS_QUEUE, 'IDLE')

            return result



    except:
        log_app.critical('Caught a global exception from the '
                         'start_app scope during app instance init, '
                         'current process will be restart',
                         exc_info=True)

        raise

    while True:

        try:

            log_app.info('the new iteration in app process was start ')

            result = app_dwnld_timer_client()

            result = app_dwnld_timer_server()


        except:
            log_app.critical('Caught a global exception from the '
                             'start_app scope during loop proceed'
                             'the current process will be restart',
                             exc_info=True)

            app.get_connection.close()
            put_in_queue(APP_STATUS_QUEUE, 'DEAD')

            raise

        else:
            log_app.info(f'The next iteration in app has been postponed for {SETTINGS.app_sleep_time}sec')
            time.sleep(SETTINGS.app_sleep_time)

