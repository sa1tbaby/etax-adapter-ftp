import time

from service import ServiceClasses, log_app

import os
from multiprocessing import Queue
from json import load

from utils.Models import ServiceSettings, Routes, FtpConnection
from service import log_app

from utils.Decorators import timer
from utils.func import put_in_queue


def start_app(
    SETTINGS: ServiceSettings,
    LISTING_PATHS: Routes,
    LISTING_SERVER_QUEUE: Queue,
    LISTING_CLIENT_QUEUE: Queue,
    APP_STATUS_QUEUE: Queue,
    CONFIG: FtpConnection,
    CONNECTION_SSL
):

    try:

        put_in_queue(APP_STATUS_QUEUE, 'SLAVE')

        func_list = dict()

        app = ServiceClasses.ServiceSender(
            settings=SETTINGS,
            listing_paths=LISTING_PATHS,
            listing_server_queue=LISTING_SERVER_QUEUE,
            listing_client_queue=LISTING_CLIENT_QUEUE,
            config=CONFIG,
            connection_ssl=CONNECTION_SSL
        )

        put_in_queue(APP_STATUS_QUEUE, 'IDLE')

        @timer(SETTINGS.model_dump(), func_list)
        def app_dwnld_timer_client():
            put_in_queue(APP_STATUS_QUEUE, 'SLAVE')

            destination = app.MODE_CLIENT
            listing = app.listing_from_server()
            result = app.send_files(destination, listing.files_list)
            log_app.info(f'Download files from server was successfully end result={result}')

            put_in_queue(APP_STATUS_QUEUE, 'IDLE')
            return result

        @timer(SETTINGS.model_dump(), func_list)
        def app_dwnld_timer_server():
            put_in_queue(APP_STATUS_QUEUE, 'SLAVE')

            destination = app.MODE_SERVER
            listing = app.listing_from_client()
            result = app.send_files(destination, listing.files_list)
            log_app.info(f'Upload files on server was successfully end result={result}')

            put_in_queue(APP_STATUS_QUEUE, 'IDLE')
            return result

        @timer(SETTINGS.model_dump(), func_list)
        def app_restart_timer():

            app.get_connection.close()

            log_app.info('app_restart_timer was triggerd '
                         'current process will be kill and restart')
            put_in_queue(APP_STATUS_QUEUE, 'DEAD')

            exit(-1073741510)

    except:
        log_app.critical('Caught a global exception from the '
                         'start_app scope during app instance init',
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
                             'the current process will be exit with '
                             '-1073741510 code and restart',
                             exc_info=True)

            app.get_connection.close()

            put_in_queue(APP_STATUS_QUEUE, 'DEAD')

            exit(-1073741510)

        else:
            app_restart_timer()

            log_app.info(f'The next iteration has been postponed for {SETTINGS.app_sleep_time}')
            time.sleep(SETTINGS.app_sleep_time)










