import os.path
from pandas import DataFrame
from pydantic import BaseModel, field_validator
from typing import List, Any
from ssl import SSLContext, PROTOCOL_TLS_SERVER
from OpenSSL.crypto import load_pkcs12, dump_certificate, dump_privatekey, FILETYPE_PEM

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
    host: Any
    time_out: int
    acct: str = None
    cert_file: str
    key_file: str

    cert_path: str = None
    cert_pass: bytes = None
    cert_obj: Any = None

    @field_validator('*')
    @classmethod
    def __none_type_validate__(cls, item):
        if item == 'None':
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
            p12 = load_pkcs12(file.read(), cls.cert_pass)

        p12_cert = dump_certificate(FILETYPE_PEM, p12.get_certificate())
        p12_key = dump_privatekey(FILETYPE_PEM, p12.get_privatekey())

        cert = SSLContext(PROTOCOL_TLS_SERVER)
        cert.load_cert_chain(certfile=p12_cert,
                             keyfile=p12_key,
                             password=None)

        return cert


class LoggerSettings(MyBaseModel):
    """
    Модель для параметров
    настройки логгера
    """

    log_level: int
    log_path: str
    file_mode: str
    output_format: str

    @field_validator('log_path')
    @classmethod
    def abspath_validate(cls, item):
        if item[0] != '/':
            item = os.path.abspath(item)
        return item


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

    script_delay_timer: int
    script_listing_timer_os: int
    script_listing_timer_ftp: int
    script_dwnld_timer: int
    script_restart_timer: int
    download_try_count: int

    @field_validator('*')
    @classmethod
    def value_type_validate(cls, item):
        if isinstance(item, str):
            item = int(item)
        return item


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






