import pandas
import logging
import re

from os.path import abspath, join
from os import walk, remove

from ssl import SSLContext
from multiprocessing import queues

from utils.FtpBaseClass import FtpManager
from utils.func import put_in_queue
from utils.Models import FtpConnection, ServiceSettings, Listing, Routes, SendParams
from utils.Decorators import timekeeper


class ServiceListing(FtpManager):

    """
    Обертка над классом FtpManager - для подключения очередей и получения листинга файлов

        * listing_server_queue: queues.Queue, - Хранит информацию о листинге с сервера
        * listing_client_queue: queues.Queue, - Хранит информацию о листинге с клиента

    """


    def __init__(
            self,
            listing_paths: Routes,
            listing_server_queue: queues.Queue,
            listing_client_queue: queues.Queue,

            config: FtpConnection,
            connection_ssl: bool | SSLContext
    ):
        FtpManager.__init__(
            self=self,
            config=config,
            connection_ssl=connection_ssl,
        )

        self.listing_paths: Routes = listing_paths
        self.listing: Listing | None = None
        self.server_queue: queues.Queue = listing_server_queue
        self.client_queue: queues.Queue = listing_client_queue

        self._log: logging.Logger = logging.getLogger(__class__.__name__)

    def listing_from_server(
            self
    ) -> bool | Listing:

        try:
            listing_server, time_spend = self._get_list(mode=self.MODE_SERVER,
                                            path=self.listing_paths.from_server_to_client.server_path)

            put_in_queue(queue=self.server_queue, message=listing_server)

        except Exception:
            self._log.critical('Ошибка при получении листинга с сервера\n!crit!\nперезапуск процесса',
                               exc_info=True)
            raise

        else:

            try:

                self._log.info(f'С сервера получен не пустой листинг \n'
                               f'time_spend={time_spend}\n'
                               f'{listing_server.files_list}')
                return listing_server

            except Exception:
                self._log.error('Ошибка при определении размера листинга с сервера',
                                exc_info=True)
                return False

    def listing_from_client(
            self
    ) -> bool | Listing:

        try:
            listing_client, time_spend = self._get_list(mode=self.MODE_CLIENT,
                                            path=self.listing_paths.from_client_to_server.client_path)

            put_in_queue(queue=self.client_queue, message=listing_client)


            self._log.info(f'С клиента получен не пустой листинг '
                           f'time_spend={time_spend}\n'
                           f'{listing_client.files_list}')

            return listing_client

        except Exception:
            self._log.error('Ошибка при получении листинга с клиента',
                            exc_info=True)
            return False

    @timekeeper
    def _get_list(
            self,
            mode: str,
            path: str
    ) -> Listing:

        try:
            self._log.debug(f'Start method _get_list, location={mode}, path={path}')

            index = 0
            files = None
            files_list = self.__create_data_frame()

            match mode:

                case self.MODE_CLIENT:
                    for directory, sub_dir, tmp_files in walk(abspath(path)):
                        files = tmp_files

                case self.MODE_SERVER:
                    # Попытка смены текущего каталога FTP
                    self.cwd(path)
                    # получаем список файлов из директории FTP
                    files = self._connection.nlst()

                    self._log.debug(f'Successfully get list of all file from server '
                                    f'count of file = {len(files)}')

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
            self._log.debug(f'Successfully create listing of files, location={mode}, '
                            f'count of file = {len(files)}')

            # save and validate listing with __validation_model: model for pandas.DataFrame listing
            self.listing = Listing(files_list=files_list)
            self._log.debug(f'Successfully validate listing of files location={mode}\n'
                            f'{self.listing.files_list}')

            return self.listing

        except Exception:
            self._log.critical(msg=f'Caught exception in get_list scope during try to get'
                                   f'list of files from location/dir={mode}/{path}',
                               exc_info=True)
            raise

    def __create_data_frame(
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

            self._log.critical(msg='Caught exception in __create_data_frame '
                                   'scope during create base DataFrame',
                               exc_info=True)
            raise

        else:

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

        ServiceListing.__init__(
            self=self,
            listing_paths=listing_paths,
            listing_server_queue=listing_server_queue,
            listing_client_queue=listing_client_queue,

            config=config,
            connection_ssl=connection_ssl
        )

        self._settings = settings
        self._log = logging.getLogger(__class__.__name__)
        self._send_params = SendParams()

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
        for key, value in params.items():
            self._send_params.__setattr__(key, value)

        try_count = 0

        try:

            self.cwd(path=self._send_params.path_server)

            self._log.debug(f'Инициализация отправки файла'
                            f'file_name={self._send_params.file_name}, '
                            f'path_client={self._send_params.path_client}, '
                            f'path_server={self._send_params.path_server}, '
                            f'destination={self._send_params.destination}')

            while try_count < self._settings.download_try_count:

                match self._send_params.destination:

                    # Отправка файла с сервера в сторону клиента
                    case self.MODE_CLIENT:

                        if (self.retr(
                                path_client=self._send_params.path_client,
                                file_name=self._send_params.file_name
                        ) and self._send_params.file_size == self.get_size(
                            mode=self._send_params.destination,
                            path=self._send_params.path_client,
                            file_name=self._send_params.file_name
                        ) and self.retr(
                            path_client=self._send_params.path_client,
                            file_name=(self._send_params.file_name + self._send_params.validator)
                        )
                        ):

                            self._log.info(f'Передача файла завершена успешно, '
                                           f'file_name={self._send_params.file_name}, '
                                           f'path_client={self._send_params.path_client}, '
                                           f'path_server={self._send_params.path_server}, '
                                           f'destination={self._send_params.destination}')
                            return True

                        else:

                            self._log.info(f'Не удалось передать файл попытка №{try_count}, '
                                           f'file_name={self._send_params.file_name}, '
                                           f'path_client={self._send_params.path_client}, '
                                           f'path_server={self._send_params.path_server}, '
                                           f'destination={self._send_params.destination}')

                            try_count += 1
                            continue

                    # Отправка файла с клиента в сторону сервера
                    case self.MODE_SERVER:


                        if (self.stor(
                            path_client=self._send_params.path_client,
                            file_name=self._send_params.file_name
                        ) and self._send_params.file_size == self.get_size(
                            mode=self._send_params.destination,
                            path=self._send_params.path_server,
                            file_name=self._send_params.file_name
                        ) and self.stor(
                            path_client=self._send_params.path_client,
                            file_name=(self._send_params.file_name + self._send_params.validator)
                        )
                        ):

                            self._log.info(f'Передача файла завершена успешно, '
                                           f'file_name={self._send_params.file_name}, '
                                           f'path_client={self._send_params.path_client}, '
                                           f'path_server={self._send_params.path_server}, '
                                           f'destination={self._send_params.destination}')
                            return True

                        else:

                            self._log.info(f'Не удалось передать файл попытка №{try_count}, '
                                           f'file_name={self._send_params.file_name}, '
                                           f'path_client={self._send_params.path_client}, '
                                           f'path_server={self._send_params.path_server}, '
                                           f'destination={self._send_params.destination}')

                            try_count += 1
                            continue

            self._log.error(f'Закончились попытки передачи файла, в текущей итерации он будет пропущен '
                            f'file_name={self._send_params.file_name}, '
                            f'path_client={self._send_params.path_client}, '
                            f'path_server={self._send_params.path_server}, '
                            f'destination={self._send_params.destination}')

            return False

        except Exception:
            self._log.critical(f'Ошибка при попытке отправки документа '
                               f'file_name={self._send_params.file_name}, '
                               f'path_client={self._send_params.path_client}, '
                               f'path_server={self._send_params.path_server}, '
                               f'destination={self._send_params.destination}')

            return False

    def del_file(
            self,
            **params
    ):
        del_params = SendParams(**params)
        #
        # Поскольку параметр destination определяет направление в котором расположен endpoint
        # то при отправке файла с FTP сервера в сторону клиента, параметр destination='client'
        # но удалить файл необходимо на стороне сервера, в связи с этим метод del_file
        # принимает параметр destination реверсивно
        #
        if del_params.destination == self.MODE_CLIENT:
            del_params.__setattr__('destination', self.MODE_SERVER)

        elif del_params.destination == self.MODE_SERVER:
            del_params.__setattr__('destination', self.MODE_CLIENT)


        try_count = 0

        while try_count < self._settings.download_try_count:

            self._log.debug(f'Попытка удаления №{try_count}, '
                            f'file_name={del_params.file_name}, '
                            f'path_client={del_params.path_client}, '
                            f'path_server={del_params.path_server}, '
                            f'destination={del_params.destination}')

            try:

                match del_params.destination:

                    case self.MODE_SERVER:
                        result = (self._connection.delete(del_params.file_name),
                                  self._connection.delete(del_params.file_name + del_params.validator))

                        self._log.debug(f'Successfully ftplib.delete({del_params.file_name}): result={result}')

                    case self.MODE_CLIENT:
                        filename = join(del_params.path_client, del_params.file_name)

                        remove(filename),
                        remove(filename+del_params.validator)

                        self._log.debug(f'Successfully os.remove {del_params.file_name}')

            except Exception:
                try_count += 1
                self._log.error(f'Ошибка при удалении файла! '
                                f'file_name={del_params.file_name}, '
                                f'path_client={del_params.path_client}, '
                                f'path_server={del_params.path_server}, '
                                f'destination={del_params.destination}')

            else:
                self._log.info(f'Удаление файла выполнено успешно, '
                                f'file_name={del_params.file_name}, '
                                f'path_client={del_params.path_client}, '
                                f'path_server={del_params.path_server}, '
                                f'destination={del_params.destination}')
                return True

        self._log.critical(f'!critical!\n'
                           f'Файл не был успешно удален, закончились попытки, '
                           f'остановка и пересоздание подпроцесса'
                           f'try_count={try_count}'
                            f'file_name={del_params.file_name}, '
                            f'path_client={del_params.path_client}, '
                            f'path_server={del_params.path_server}, '
                            f'destination={del_params.destination}')

        raise Exception

    def send_files(
            self,
            destination,
            files_list: Listing | bool
    ):

        try:

            if type(files_list) != Listing:
                return True

            files_list: pandas.DataFrame = files_list.files_list

            kwargs = dict()
            kwargs.update({'validator': self._settings.validator,
                           'destination': destination})

            if files_list.empty:
                self._log.info(f'С сервера получен пустой листинг')
                return True

            if destination == self.MODE_SERVER:
                kwargs.update({'path_client': self.listing_paths.from_client_to_server.client_path})
                kwargs.update({'path_server': self.listing_paths.from_client_to_server.server_path})

            elif destination == self.MODE_CLIENT:
                kwargs.update({'path_client': self.listing_paths.from_server_to_client.client_path})
                kwargs.update({'path_server': self.listing_paths.from_server_to_client.server_path})

            else:
                return False

            for index, row in files_list.iterrows():

                kwargs.update({'file_name': row['file_name'],
                               'file_size': row['file_size']})

                if self.send_file(**kwargs) and not row['control_check']:

                    files_list.loc[index, 'control_check'] = self.del_file(**kwargs)
                    self._log.info(f'Отправка документа {row["file_name"]} завершена успешно')

                else:
                    #CHANGEMETHOD!!!!!!!!!!!!!!!!!!!!!!!
                    return files_list.count()

        except:
            self._log.critical('',exc_info=True)
        else:
            self._log.info(f'Upload files was successfully end ')
            return True

