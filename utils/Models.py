import os.path

import pandas
from pandas import DataFrame
from pydantic import BaseModel, field_validator
from typing import List, Any
from ssl import SSLContext, PROTOCOL_TLS_SERVER
from OpenSSL.crypto import FILETYPE_PEM, load_certificate, load_privatekey, dump_certificate, dump_privatekey
from dataclasses import dataclass



@dataclass
class SendParams:
    path_client: str = None
    path_server: str = None
    file_name: str = None
    file_size: int = None
    validator: str = None
    destination: str = None

class MyBaseModel(BaseModel):
    """
    the basic model from which the rest are inherited
    contains a field with logger messages configuration
    """

    class Config:
        validate_assignment = True


class FtpConnection(MyBaseModel):
    """
    Модель для параметров
    подключения к FTP серверу

    cert_: Параметры сертификата для fTPS подключения
    Валидация cert_obj происходит в случае передачи типа отличного от SSLcontext
    в таком случае возвращается новый объект типа SSLcontext с подгруженным сертификатом
    по пути: sert_path с паролем: cert_pass
    """

    password: str
    user_name: str
    host: str
    time_out: int
    acct: str = None

    cert_key: str = None
    cert_path: str = None
    cert_pass: str = None
    cert_obj: Any = None

    @field_validator('*')
    @classmethod
    def __none_type_validate__(cls, item):
        if item == 'None' or '':
            return None
        return item

    @field_validator('cert_path')
    @classmethod
    def abspath_validate(cls, item):
        if item[0] != '/':
            item = os.path.abspath(item)
        return item

    @field_validator('cert_obj')
    @classmethod
    def cert_validator(
            cls, item
    ) -> Any:

        if type(item) is SSLContext:
            return item

        with open(cls.cert_path, 'rb') as file:
            PEM_cert = dump_certificate(
                FILETYPE_PEM,
                load_certificate(FILETYPE_PEM, file.read())
            )

        with (open(cls.cert_key, 'rb') as file):
            PEM_key = dump_privatekey(
                FILETYPE_PEM,
                load_privatekey(FILETYPE_PEM, file.read())
            )

        cert = SSLContext(PROTOCOL_TLS_SERVER)
        cert.load_cert_chain(certfile=PEM_cert,
                             keyfile=PEM_key,
                             password=cls.cert_pass)

        return cert


class LoggerSettings(MyBaseModel):
    """
    Модель для параметров
    настройки логгера
    """

    level: int
    filename: list
    filemode: str
    format: str


class Directories(MyBaseModel):
    """
    Модель для более контролируемого указания,
    какие директории используются на стороне сервера и на стороне клиента,
    в дальнейшем модель используется, как поле для модели хранящей пути
    """

    client_path: str
    server_path: str

    @field_validator('*')
    @classmethod
    def abspath_validate(cls, item):
        if item[0] != '/':
            item = os.path.abspath(item)
        return item


class Routes(MyBaseModel):
    """
    Модель для хранения различных путей обмена сообщениями
    """

    from_client_to_server: Directories
    from_server_to_client: Directories


class ServiceSettings(MyBaseModel):
    """
    Модель для хранения настроек бизнес логики самого сервиса
    """

    main_health_check_timer: int
    app_dwnld_timer_client: int
    app_dwnld_timer_server: int
    app_sleep_time: int
    app_restart_timer: int
    download_try_count: int
    validator: str


class Listing(MyBaseModel):
    """
    Модель для хранения и валидации листинга
    """

    files_list: List | None

    @field_validator('files_list')
    @classmethod
    def done_file_validate(
            cls,
            files_list: DataFrame
    ) -> DataFrame | None:

        if files_list.empty:
            return None

        sorted_len = len(files_list) - 1

        # Итерируем конечный список
        for iteration, file_name in enumerate(files_list['file_name']):

            # Дропаем последний элемент. С точки зрения логики работы
            # он всегда будет дубликатом
            if iteration == sorted_len:
                files_list.drop([iteration], inplace=True)
                continue

            # Скипаем первый элемент, если второй является его дубликатом
            if file_name == files_list.loc[iteration + 1, 'file_name']:
                continue

            if files_list.loc[iteration, 'file_size'] == -1:
                files_list.drop([iteration], inplace=True)

            # Удаляем первый элемент, если он не соответствует второму
            else:
                files_list.drop([iteration], inplace=True)

        # Сбрасываем индексы
        files_list.reset_index(drop=True, inplace=True)

        return files_list






