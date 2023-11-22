from service import ServiceClasses, log_app

import os
from multiprocessing import Queue
from json import load

from utils.Models import ServiceSettings, Routes, FtpConnection
from service import log_app

from utils.Decorators import timer


def start_app(
    SETTINGS: ServiceSettings,
    LISTING_PATHS: Routes,
    LISTING_SERVER_QUEUE: Queue,
    LISTING_CLIENT_QUEUE: Queue,
    CONFIG: FtpConnection,
    CONNECTION_SSL
):

    func_list = dict()

    app = ServiceClasses.ServiceSender(
        settings=SETTINGS,
        listing_paths=LISTING_PATHS,
        listing_server_queue=LISTING_SERVER_QUEUE,
        listing_client_queue=LISTING_CLIENT_QUEUE,
        config=CONFIG,
        connection_ssl=CONNECTION_SSL
    )

    while True:

        log_app.info('В процессе обработчика начата новая итерация')
        @timer(SETTINGS.model_dump(), func_list)
        def dwnld_timer_client():
            destination = app.MODE_CLIENT
            listing = app.listing_from_server()
            return app.send_files(destination, listing.files_list)

        @timer(SETTINGS.model_dump(), func_list)
        def dwnld_timer_server():
            destination = app.MODE_SERVER
            listing = app.listing_from_client()
            return app.send_files(destination, listing.files_list)

        result, func_list = dwnld_timer_client()
        log_app.info(f'Завершена загрузка файлов с сервера статус={result}')

        result, func_list = dwnld_timer_server()
        log_app.info(f'Завершена отправка файлов на сервер статус={result}')









