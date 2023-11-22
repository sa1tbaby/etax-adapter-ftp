import logging
from multiprocessing.queues import Queue
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