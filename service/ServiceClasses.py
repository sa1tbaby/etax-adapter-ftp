import pandas
import time
import logging
import re

from dataclasses import dataclass

import os.path
from os import walk, remove

from ssl import SSLContext
from multiprocessing import queues

from utils.FTP import FtpBaseClass
from utils.func import put_in_queue
from utils.models import FtpConnection, ServiceSettings, Listing, Routes


class ServiceListing(FtpBaseClass):

    def __init__(
            self,
            listing_paths: Routes,
            listing_server_queue: queues.Queue,
            listing_client_queue: queues.Queue,

            config: FtpConnection,
            connection_ssl: bool | SSLContext
    ):
        super().__init__(
            config=config,
            connection_ssl=connection_ssl,
        )

        self.listing_paths: Routes = listing_paths
        self.listing: Listing | None = None
        self.server_queue: queues.Queue = listing_server_queue
        self.client_queue: queues.Queue = listing_client_queue

        self._log: logging.Logger = logging.getLogger(__class__.__name__)

    def from_server(
            self
    ) -> bool | Listing:

        try:
            listing_server = self.__get_list(mode=self.mode_server,
                                             path=self.listing_paths.from_server_to_client.server_path)

            put_in_queue(queue=self.server_queue, message=listing_server)

        except Exception:
            self._log.critical('Ошибка при получении листинга с сервера\n!crit!\nперезапуск процесса',
                               exc_info=True)
            raise

        else:

            try:
                if listing_server.files_list is None:
                    self._log.info(f'С сервера получен пустой листинг')
                    return False

                else:
                    self._log.info(f'С сервера получен не пустой листинг \n'
                                   f'{listing_server.files_list}')
                    return listing_server

            except Exception:
                self._log.error('Ошибка при определении размера листинга с сервера',
                                exc_info=True)
                return False

    def from_client(
            self
    ) -> bool | Listing:

        try:
            listing_client = self.__get_list(mode=self.mode_client,
                                             path=self.listing_paths.from_client_to_server.client_path)

            put_in_queue(queue=self.client_queue, message=listing_client)

            if listing_client.files_list is None:
                self._log.info(f'С клиента получен пустой листинг')
                return False

            else:
                self._log.info(f'С клиента получен не пустой листинг \n'
                               f'{listing_client.files_list}')
                return listing_client

        except Exception:
            self._log.error('Ошибка при получении листинга с клиента',
                            exc_info=True)
            return False

    def __get_list(
            self,
            mode: str,
            path: str
    ) -> Listing:

        try:

            index = 0
            start_time = time.time()
            files = None
            files_list = self.__crate_data_frame()

            match mode:

                case self.mode_client:
                    for directory, sub_dir, tmp_files in walk(os.path.abspath(path)):
                        files = tmp_files

                case self.mode_server:
                    # Попытка смены текущего каталога FTP
                    self.cwd(path)
                    # получаем список файлов из директории FTP
                    files = self._connection.nlst()

                    self._log.debug(f'{self.__config_log["INFO_06"]} {len(files)}')

            for iteration, file_name in enumerate(files):

                # Если файл подходит по маске, убираем .done часть
                # Создавая тем самым дубликат в самом листинге
                if re.findall(r'.zip.done$', file_name):
                    file_name = file_name[:-5]

                elif not re.findall(r'.zip$', file_name):
                    continue

                files_list.loc[index, 'file_name'] = file_name
                files_list.loc[index, 'control_check'] = False
                files_list.loc[index, 'file_size'] = self.get_size(mode=mode, file_name=file_name, path=path)
                index += 1

            # Сортируем список
            files_list.sort_values(by='file_name', ascending=True, inplace=True)

            # save and validate listing with __validation_model: model for pandas.DataFrame listing
            self.listing = Listing(files_list=files_list)

            self._log.info(f'{self.__config_log["INFO_01"]}{mode}/{int(time.time() - start_time)}sec')

            return self.listing

        except Exception:
            self._log.critical(msg=f'{self.__config_log["CRITICAL_01"]}{mode}/{path}',
                               exc_info=True)
            raise

    def __crate_data_frame(
            self,
            index='file_name'
    ) -> pandas.DataFrame:

        try:

            files_list = pandas.DataFrame(
                columns=[
                    'file_name',
                    'file_size',
                    'control_check'
                ]
            )

            files_list.astype(
                {
                    'file_name': str,
                    'file_size': int,
                    'control_check': bool
                }
            )

            files_list.set_index(index)

        except Exception:

            self._log.critical(msg=self.__config_log["ERROR_03"],
                               exc_info=True)
            raise

        else:
            self._log.debug(msg=self.__config_log["DEBUG_01"])
            return files_list


class ServiceSender(ServiceListing):

    def __init__(
            self,
            # Params for an instance of the ServiceSender current class
            settings: ServiceSettings,

            # Params for an instance of the ServiceListing parent class
            listing_paths: Routes,
            listing_server_queue: queues.Queue,
            listing_client_queue: queues.Queue,

            # Params for an instance of the ManagerFTP parent class
            config: FtpConnection,
            connection_ssl: bool | SSLContext
    ):
        super().__init__(
            listing_paths=listing_paths,
            listing_server_queue=listing_server_queue,
            listing_client_queue=listing_client_queue,

            config=config,
            connection_ssl=connection_ssl
        )

        self._settings = settings
        self._log = logging.getLogger(__class__.__name__)

    @dataclass
    class SendParams:
        destination: str
        path_client: str
        path_server: str
        file_name: str
        file_size: str
        validator: str

    def send_file(
            self,
            **params,

    ) -> bool:
        """
        Функция выполняет отправку и проверку файла по условию:

        * Отправка file_name
        * Сравнение file_size с размером файла в destination
        * Отправка валидационного файла*

         Каждый пункт условия представляет собой метод родительского класса,
         если один из этапов вернет false, остальные проверятся не будут,
         увеличится счетчик попыток и начнется новая итерация.
            *В бизнес процессе, валидация окончательной загрузки файла, происходит при наличии директории пустого файла
        с таким же именем и дополнительным параметром в расширении

        * destination: параметр, определяющий кому будет отправлен файл, клиенту или серверу
        * path_client: директория, настроенная на ЭДО на стороне клиента
        * path_server: директория, настроенная на ЭДО на стороне FTP сервера
        * file_name: название файла
        * file_size: исходный размер файла
        * validator: параметр валидационного файла

        :return: True в случае прохождения проверки | False в случае превышения
        максимально допустимого кол-ва попыток отправки
        """

        #
        self.SendParams(**params)

        try_count = 0

        try:

            self.cwd(path=self.SendParams.path_server)

            while try_count < self._settings.download_try_count:

                self._log.debug(f'Инициализация отправки файла №{try_count}, '
                                f'file_name={self.SendParams.file_name}, '
                                f'path_client={self.SendParams.path_client}, '
                                f'path_server={self.SendParams.path_server}, '
                                f'destination={self.SendParams.destination}')

                match self.SendParams.destination:

                    # Отправка файла с сервера в сторону клиента
                    case self.mode_client:

                        if (self.retr(
                                path=self.SendParams.path_client,
                                file_name=self.SendParams.file_name
                        ) and self.SendParams.file_size == self.get_size(
                            mode=self.SendParams.destination,
                            path=self.SendParams.path_client,
                            file_name=self.SendParams.file_name
                        ) and self.retr(
                            path=self.SendParams.path_client,
                            file_name=(self.SendParams.file_name + self.SendParams.validator)
                        )
                        ):

                            self._log.info(f'Передача файла завершена успешно, '
                                           f'file_name={self.SendParams.file_name}, '
                                           f'path_client={self.SendParams.path_client}, '
                                           f'path_server={self.SendParams.path_server}, '
                                           f'destination={self.SendParams.destination}')
                            return True

                        else:

                            self._log.info(f'Не удалось передать файл попытка №{try_count}, '
                                           f'file_name={self.SendParams.file_name}, '
                                           f'path_client={self.SendParams.path_client}, '
                                           f'path_server={self.SendParams.path_server}, '
                                           f'destination={self.SendParams.destination}')

                            try_count += 1

                    # Отправка файла с клиента в сторону сервера
                    case self.mode_server:

                        if (self.stor(
                            path=self.SendParams.path_server,
                            file_name=self.SendParams.file_name
                        ) and self.SendParams.file_name == self.get_size(
                            mode=self.SendParams.destination,
                            path=self.SendParams.path_server,
                            file_name=self.SendParams.file_name
                        ) and self.stor(
                            path=self.SendParams.path_server,
                            file_name=(self.SendParams.file_name + self.SendParams.validator)
                        )
                        ):

                            self._log.info(f'Передача файла завершена успешно, '
                                           f'file_name={self.SendParams.file_name}, '
                                           f'path_client={self.SendParams.path_client}, '
                                           f'path_server={self.SendParams.path_server}, '
                                           f'destination={self.SendParams.destination}')
                            return True

                        else:

                            self._log.info(f'Не удалось передать файл попытка №{try_count}, '
                                           f'file_name={self.SendParams.file_name}, '
                                           f'path_client={self.SendParams.path_client}, '
                                           f'path_server={self.SendParams.path_server}, '
                                           f'destination={self.SendParams.destination}')

                            try_count += 1

            self._log.error(f'Закончились попытки передачи файла, в текущей итерации он будет пропущен '
                            f'file_name={self.SendParams.file_name}, '
                            f'path_client={self.SendParams.path_client}, '
                            f'path_server={self.SendParams.path_server}, '
                            f'destination={self.SendParams.destination}')

            return False

        except Exception:
            self._log.critical(f'Ошибка при попытке отправки документа '
                               f'file_name={self.SendParams.file_name}, '
                               f'path_client={self.SendParams.path_client}, '
                               f'path_server={self.SendParams.path_server}, '
                               f'destination={self.SendParams.destination}')

    def del_file(
            self,
            doc_name,
            path_from,
            mode
    ):

        try_count = 0

        while try_count < self._settings.download_try_count:

            self._log.debug(f'Попытка удаления №{try_count}, '
                            f'file_name={doc_name}, '
                            f'path={path_from}, '
                            f'mode={mode}')

            try:
                match mode:

                    case self.mode_server:
                        result = self._connection.delete(doc_name)
                        self._log.debug(f'ftplib.delete(doc_name): result={result}')

                    case self.mode_client:
                        remove(os.path.join(path_from, doc_name))

            except Exception:
                try_count += 1
                self._log.error(f'Ошибка при удалении файла! '
                                f'try_count={try_count}'
                                f'file_name={doc_name}, '
                                f'path={path_from}, '
                                f'mode={mode}')

            else:
                self._log.info(f'Удаление файла выполнено успешно, '
                               f'file_name={doc_name}, '
                               f'path={path_from}, '
                               f'mode={mode}')
                return True

        self._log.critical(f'!critical!\n'
                           f'Файл не был успешно удален, закончились попытки, остановка и пересоздание подпроцесса'
                           f'try_count={try_count}'
                           f'file_name={doc_name}, '
                           f'path={path_from}, '
                           f'mode={mode}')

        raise Exception

    def send_files(
            self,
            destination,
            path_server,

    ):
