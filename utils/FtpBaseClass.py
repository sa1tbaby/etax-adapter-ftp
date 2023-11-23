import ftplib
import logging

from os.path import getsize, join

from ssl import SSLContext
from utils.Models import FtpConnection


class FtpManager:

    # Параметры используемые для системного вызова методов внутри самого класса
    MODE_CLIENT = 'client'
    MODE_SERVER = 'server'

    """
        Класс для работы с FTP

        * def cwd - смена каталога
        * def get_size - Получение размера файла
        * def stor - Отправка документа на FTP
        * def retr - Получение документа с FTP
        * def _check_path -
        * def _connect_ftp -
        * def _get_list - 
        * def __crate_data_frame -  
        
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
        self._config: FtpConnection = config
        self._log: logging.Logger = logging.getLogger(__class__.__name__)
        self._connection: ftplib.FTP | ftplib.FTP_TLS = self._connect_ftp(connection_ssl)

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
            if self._check_path(path=path):
                self._connection.cwd(path)
                self._log.info(f'Current directory successfully changed to {path}')

        except Exception:
            # raised when an unexpected reply is received from the server.
            self._log.critical(msg='Something wet wrong when FTP manager try to change ftp directory',
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

        :param mode: Параметр среды, FTP server или OS client
        :param path: По умолчанию None, требуется только для mode='os'
        :param file_name:
        :return: size: int, -1 при неудаче
        """

        match mode:

            case self.MODE_SERVER:

                try:
                    return self._connection.size(file_name)

                except Exception:
                    self._log.error(msg=f'Something wet wrong when FTP manager try to get size '
                                        f'of file {file_name}, from FTP server ', exc_info=True)
                    return -1

            case self.MODE_CLIENT:

                try:

                    return getsize(
                        join(path, file_name)
                    )

                except Exception:
                    self._log.error(msg=f'Something wet wrong when FTP manager try to get size'
                                        f'of file {file_name}, from client OS ', exc_info=True)
                    return -1

    def retr(
            self,
            path_client,
            file_name
    ) -> bool:
        """
        Переопределение метода retr либы ftplib, для скачивания файла с FTP сервера
        Метод принимает путь к файлу для сохранения на стороне клиента и имя файла
        Файл сохраняется с таким же именем с которым он был на сервер

        :param path_client:
        :param file_name:
        :return:
        """

        try:

            with open(
                    join(path_client, file_name),
                    'wb'
            ) as file:

                try:

                    self._connection.retrbinary(f"RETR {file_name}", file.write)

                except Exception:
                    self._log.error(msg=f'Something wet wrong when FTP manager try to retrieve data in binary format'
                                        f'from file {file_name}, in FTP server to OS client', exc_info=True)
                    return False

        except Exception:

            self._log.error(msg=f'Something wet wrong when FTP manager try to download file '
                                f'{file_name} from FTP server and record in OS client', exc_info=True)
            return False

        else:
            return True

    def stor(
            self,
            path_client,
            file_name
    ) -> bool:
        """

        :param path_client: принимает путь к файлу на стороне клиента
        :param file_name:
        :return:
        """

        try:

            with open(
                    join(path_client, file_name),
                    'rb'
            ) as file:

                try:

                    self._connection.storbinary(f"STOR {file_name}", file)

                except Exception:

                    self._log.error(msg=f'Something wet wrong when FTP manager try to store data in binary format'
                                        f'from file {file_name}, on OS client server to FTP server', exc_info=True)
                    return False

        except Exception:

            self._log.error(msg=f'Something wet wrong when FTP manager try to upload file '
                                f'{file_name} from OS client and record in FTP server', exc_info=True)
            return False

        else:
            return True

    def _check_path(
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

                self._log.debug(msg=f'Current ftp dir has matches with dir  {path}')
                return False

        except Exception:
            self._log.critical(msg='Caught exception in _check_path scope during '
                                   'try to compare cur and next path',
                               exc_info=True)
            raise

    def _connect_ftp(
            self,
            connection_ssl: bool | SSLContext
    ) -> ftplib.FTP | ftplib.FTP_TLS:

        if connection_ssl:

            try:
                connection = ftplib.FTP_TLS(
                    host=self._config.host,
                    user=self._config.user_name,
                    passwd=self._config.password,
                    acct=self._config.acct,
                    timeout=self._config.time_out,
                    certfile=self._config.cert_file,
                    keyfile=self._config.key_file,
                    context=connection_ssl
                )

                connection.prot_p()

                self._log.info(f'FTP over TLS connection was successfully established'
                               f'\n{connection.welcome}'
                               f'\n{connection.port}'
                               f'\n{connection.sock}'
                               f'\n{connection.lastresp}')

                return connection

            except Exception:

                self._log.critical(msg='Caught exception in _connect_ftp scope '
                                       'during try to established FTP TLS connection ',
                                   exc_info=True)
                raise

        else:

            try:
                connection = ftplib.FTP(
                    host=self._config.host,
                    user=self._config.user_name,
                    passwd=self._config.password,
                    acct=self._config.acct,
                    timeout=self._config.time_out
                )

                self._log.info(f'FTP connection was successfully established'
                               f'\n{connection.welcome}'
                               f'\n{connection.port}'
                               f'\n{connection.sock}'
                               f'\n{connection.lastresp}')

                return connection

            except Exception:

                self._log.critical(msg='Caught exception in _connect_ftp scope '
                                       'during try to established FTP connection ',
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
        return self._config

