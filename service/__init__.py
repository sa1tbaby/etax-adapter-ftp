import logging

LOG_FILE = 'log.txt'
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "__%(name)s__: %(asctime)s __%(levelname)s__   \n%(message)s"

logging.basicConfig(
    level=LOG_LEVEL,
    filename=LOG_FILE,
    filemode='a',
    format=LOG_FORMAT
)

log_app = logging.getLogger('app')