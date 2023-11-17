from multiprocessing.queues import Queue
from typing import Any

def put_in_queue(
        queue: Queue,
        message: Any
) -> None:
    try:

        while not queue.empty():
            tmp_message = queue.get()
            del tmp_message

        queue.put(message)

    except Exception:
        log_script.critical(msg='Ошибка при работе с очередью',
                            exc_info=True)
        raise