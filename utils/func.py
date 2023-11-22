import logging
from multiprocessing.queues import Queue
from multiprocessing import Process
from typing import Any

def put_in_queue(
        queue: Queue,
        message: Any
) -> None:

    log = logging.getLogger('put_in_queue')

    try:

        while not queue.empty():
            tmp_message = queue.get()
            del tmp_message

        queue.put(message)

    except Exception:
        log.critical(msg='Ошибка при работе с очередью',
                            exc_info=True)
        raise

def script_status(process: Process | bool,
                  status_queue: Queue):

    log = logging.getLogger('script_status')

    def check_put(
            queue
    ) -> None:

        tmp = True

        while not queue.empty():
            tmp = queue.get()

        return tmp

    if check_put(status_queue) == 'dead':
        log.debug(f'process status dead')
        return False

    else:
        log.info(f'process status {process.is_alive()}')
        return process.is_alive()