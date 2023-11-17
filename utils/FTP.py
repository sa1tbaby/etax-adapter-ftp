import ftplib
import logging

from os.path import getsize, join

from ssl import SSLContext
from utils.models import FtpConnection


class FtpBaseClass:

    # Параметры используемые для системного вызова методов внутри самого класса
    mode_client = 'client'
    mode_server = 'server'

    """
        Класс для работы с FTP

        * def cwd - смена каталога
        * def get_list_from_os - получение листинга документов из ос
        * def get_list_from_ftp - получение листинга документов из FTP
        * def get_size - Получение размера файла
        * def retr - Получение документа с FTP
        * def stor - Отправка документа на FTP
        """

    def __init__(
            self,
            config: FtpConnection,
            connection_ssl: bool = False
    ) -> None:

        """
        :param config: Принимает экземпляр класса модели pydantic,
            с конфигурацией подключения к FTP серверу

        :param connection_ssl: Параметр защищенного подключения к FTP серверу
        """

        self._log: logging.Logger = logging.getLogger(__class__.__name__)
        self._connection: ftplib.FTP | ftplib.FTP_TLS = self.__connect_ftp(connection_ssl)

        self.__config: FtpConnection = config
        self.__config_log: dict = config.config_log

    def __new__(
            cls,
            *args,
            **kwargs
    ):
        if not hasattr(cls, '__instance'):
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def cwd(
            self,
            path: str
    ) -> None:
        """
        В случае попытки смены каталога FTP сервера на текущий будет выброшена 550 ошибка библиотекой ftplib
        Метод необходим для проверки несоответсвия текущего каталога FTP сервера с тем в который перемещаемся

        :param path: Путь к каталогу FTP в который необходимо переместиться
        :return: None
        """

        try:

            # Меняем директорию FTP, на необходимый каталог, если мы уже не в нем
            if self.__check_path(path=path):
                self._connection.cwd(path)
                self._log.info(f'{self.__config_log["INFO_03"]} {path}')

        except Exception:
            # raised when an unexpected reply is received from the server.
            self._log.critical(msg=self.__config_log["CRITICAL_02"],
                               exc_info=True)

            raise

    def get_size(
            self,
            mode: str,
            file_name,
            path=None
    ) -> int:

        """
        При вызове метода с параметром mode='server' необходимо убедиться,
        что текущая директория FTP адаптера, совпадает с той
        в которой находится файл file_name='file_name'

        :param mode: Параметр среды, FTP или OS
        :param path: По умолчанию None, требуется только для mode='os'
        :param file_name:
        :return: size: int, -1 при неудаче
        """

        match mode:

            case self.mode_server:

                try:
                    return self._connection.size(file_name)

                except Exception:
                    self._log.error(msg=f'{self.__config_log["ERROR_04"]} {file_name}', exc_info=True)
                    return -1

            case self.mode_client:

                try:

                    return getsize(
                        join(path, file_name)
                    )

                except Exception:
                    self._log.error(msg=f'{self.__config_log["ERROR_05"]} {file_name}',
                                    exc_info=True)
                    return -1

    def retr(
            self,
            path,
            file_name
    ) -> bool:
        """
        Переопределение метода retr либы ftplib, для скачивания файла с FTP сервера
        Метод принимает путь к файлу для сохранения на стороне клиента и имя файла
        Файл сохраняется с таким же именем с которым он
        и загружается на сервер

        :param path:
        :param file_name:
        :return:
        """

        try:

            with open(
                    join(path, file_name),
                    'wb'
            ) as file:

                try:
                    self._connection.retrbinary(f"RETR {file_name}", file.write)

                except Exception:
                    self._log.error(msg=f'{self.__config_log["ERROR_06"]} {file_name}',
                                    exc_info=True)
                    return False

        except Exception:

            self._log.error(msg=f'{self.__config_log["ERROR_07"]}\n{join(path, file_name)}',
                            exc_info=True)
            return False

        else:
            return True

    def stor(
            self,
            path,
            file_name
    ) -> bool:
        """

        :param path:
        :param file_name:
        :return:
        """

        try:

            with open(
                    join(path, file_name),
                    'rb'
            ) as file:

                try:

                    self._connection.storbinary(f"STOR {file_name}", file)

                except Exception:

                    self._log.error(msg=f'{self.__config_log["ERROR_08"]} {file_name}',
                                    exc_info=True)
                    return False

        except Exception:

            self._log.error(msg=f'{self.__config_log["ERROR_09"]}\n{join(path, file_name)}',
                            exc_info=True)
            return False

        else:
            return True

    def __check_path(
            self,
            path
    ) -> bool:
        """
        Функция проверки совпадения каталогов,
        поскольку в случае попытки смены текущего каталога на такой-же
        выбрасывается исключение 550, ftplib.error_perm

        :param path:
        :return:
        """
        try:

            if path != self._connection.pwd():
                return True

            else:

                self._log.debug(msg=f'{self.__config_log["DEBUG_02"]} {path}')
                return False

        except Exception:
            self._log.critical(msg=self.__config_log["CRITICAL_03"],
                               exc_info=True)
            raise

    def __connect_ftp(
            self,
            connection_ssl: bool | SSLContext
    ) -> ftplib.FTP | ftplib.FTP_TLS:

        if connection_ssl is bool:

            try:

                connection = ftplib.FTP(
                    host=self.__config.host,
                    user=self.__config.user_name,
                    passwd=self.__config.password,
                    acct=self.__config.acct,
                    timeout=self.__config.time_out
                )

                self._log.info(f'{self.__config_log["INFO_04"]}'
                               f'\n{connection.welcome}'
                               f'\n{connection.port}'
                               f'\n{connection.sock}'
                               f'\n{connection.lastresp}')

                return connection

            except Exception:

                self._log.critical(msg=self.__config_log["CRITICAL_04"],
                                   exc_info=True)
                raise

        else:

            try:

                connection = ftplib.FTP_TLS(
                    host=self.__config.host,
                    user=self.__config.user_name,
                    passwd=self.__config.password,
                    acct=self.__config.acct,
                    timeout=self.__config.time_out,
                    certfile=self.__config.cert_file,
                    keyfile=self.__config.key_file,
                    context=connection_ssl
                )

                connection.prot_p()

                self._log.info(f'{self.__config_log["INFO_05"]}'
                               f'\n{connection.welcome}'
                               f'\n{connection.port}'
                               f'\n{connection.sock}'
                               f'\n{connection.lastresp}')

                return connection

            except Exception:

                self._log.critical(msg=self.__config_log["CRITICAL_05"],
                                   exc_info=True)
                raise

    @property
    def get_connection(
            self
    ):
        return self._connection

    @property
    def get_config(
            self
    ):
        return self.__config

